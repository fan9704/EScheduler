import re
from datetime import datetime, timedelta
from typing import List
from zoneinfo import ZoneInfo

from croniter import croniter

from src.configs import TZ
from src.models.pydantic.schedule_helper import (
    ScheduleType, CronField,
    RateExpressionRequest, CronExpressionRequest, QuickScheduleRequest,
    ScheduleExpressionResponse, ScheduleValidationRequest, ScheduleValidationResponse,
    ScheduleTemplateResponse, CronHelpResponse
)
from src.utils.logger import logger
from src.consts import CRON_FIELD_COUNT


class ScheduleHelperService:
    """排程表達式輔助服務"""
    
    def __init__(self):
        self.quick_schedules = {
            "every_minute": {"expression": "rate(1 minute)", "description": "每分鐘執行"},
            "every_5_minutes": {"expression": "rate(5 minutes)", "description": "每5分鐘執行"},
            "every_hour": {"expression": "rate(1 hour)", "description": "每小時執行"},
            "every_day": {"expression": "cron(0 0 * * *)", "description": "每天午夜執行"},
            "workdays_9am": {"expression": "cron(0 9 * * 1-5)", "description": "工作日早上9點執行"},
            "weekend_backup": {"expression": "cron(0 2 * * 0)", "description": "週日凌晨2點執行"},
            "monthly_report": {"expression": "cron(0 9 1 * *)", "description": "每月1號早上9點執行"}
        }
        self.tz = ZoneInfo(TZ)
    
    async def generate_rate_expression(self, request: RateExpressionRequest) -> ScheduleExpressionResponse:
        """生成 Rate 表達式"""
        expression = f"rate({request.value} {request.unit.value})"
        
        # 生成描述
        unit_zh = {
            "second": "秒鐘", "seconds": "秒鐘",
            "minute": "分鐘", "minutes": "分鐘",
            "hour": "小時", "hours": "小時",
            "day": "天", "days": "天"
        }
        description = f"每{request.value}{unit_zh.get(request.unit, request.unit)}執行一次"
        
        # 計算接下來的執行時間
        next_runs = self._calculate_next_runs_rate(request.value, request.unit)
        
        return ScheduleExpressionResponse(
            expression=expression,
            type=ScheduleType.RATE,
            description=description,
            next_runs=next_runs
        )
    
    async def generate_cron_expression(self, request: CronExpressionRequest) -> ScheduleExpressionResponse:
        """生成 Cron 表達式"""
        expression = f"cron({request.minute} {request.hour} {request.day} {request.month} {request.weekday})"
        
        # 生成描述
        description = self._generate_cron_description(request)
        
        # 計算接下來的執行時間
        next_runs = self._calculate_next_runs_cron(expression)
        
        return ScheduleExpressionResponse(
            expression=expression,
            type=ScheduleType.CRON,
            description=description,
            next_runs=next_runs
        )
    
    async def generate_quick_schedule(self, request: QuickScheduleRequest) -> ScheduleExpressionResponse:
        """生成快速排程表達式"""
        if request.type in self.quick_schedules:
            template = self.quick_schedules[request.type]
            return ScheduleExpressionResponse(
                expression=template["expression"],
                type=ScheduleType.CRON if template["expression"].startswith("cron") else ScheduleType.RATE,
                description=template["description"],
                next_runs=self._calculate_next_runs_from_expression(template["expression"])
            )
        
        # 自定義快速排程
        if request.type == "custom_time" and request.time:
            hour, minute = request.time.split(":")
            weekdays = ",".join(map(str, request.weekdays)) if request.weekdays else "*"
            expression = f"cron({minute} {hour} * * {weekdays})"
            description = f"每天{request.time}執行" if not request.weekdays else f"指定星期{request.time}執行"
            
            return ScheduleExpressionResponse(
                expression=expression,
                type=ScheduleType.CRON,
                description=description,
                next_runs=self._calculate_next_runs_cron(expression)
            )
        
        elif request.type == "custom_interval" and request.interval and request.unit:
            expression = f"rate({request.interval} {request.unit})"
            description = f"每{request.interval}{request.unit}執行一次"
            
            return ScheduleExpressionResponse(
                expression=expression,
                type=ScheduleType.RATE,
                description=description,
                next_runs=self._calculate_next_runs_rate(request.interval, request.unit)
            )
        
        raise ValueError("無效的快速排程類型")

    async def validate_expression(self, request: ScheduleValidationRequest) -> ScheduleValidationResponse:
        """驗證排程表達式"""
        expression = request.expression.strip()

        try:
            if expression.startswith('cron(') and expression.endswith(')'):
                return self._validate_cron(expression)

            if expression.startswith('rate(') and expression.endswith(')'):
                return self._validate_rate(expression)

            return ScheduleValidationResponse(
                valid=False,
                error="表達式必須以 'cron(' 或 'rate(' 開頭"
            )

        except Exception as e:
            return ScheduleValidationResponse(
                valid=False,
                error=f"表達式驗證失敗: {str(e)}"
            )

    def _validate_cron(self, expression: str) -> ScheduleValidationResponse:
        """內部方法：驗證 Cron 邏輯"""
        cron_expr = expression[5:-1]
        parts = cron_expr.split()

        if len(parts) != CRON_FIELD_COUNT:
            return ScheduleValidationResponse(
                valid=False,
                error="Cron 表達式必須包含5個部分：分 時 日 月 週"
            )

        # 測試 croniter 是否能解析
        croniter(cron_expr, datetime.now(self.tz))

        return ScheduleValidationResponse(
            valid=True,
            type=ScheduleType.CRON,
            description=self._generate_cron_description_from_parts(parts),
            next_runs=self._calculate_next_runs_cron(expression)
        )

    def _validate_rate(self, expression: str) -> ScheduleValidationResponse:
        """內部方法：驗證 Rate 邏輯"""
        rate_expr = expression[5:-1]
        match = re.match(r'(\d+)\s+(minute|minutes|hour|hours|day|days)', rate_expr)

        if not match:
            return ScheduleValidationResponse(
                valid=False,
                error="Rate 表達式格式錯誤，應為：rate(數值 單位)"
            )

        value_str, unit = match.groups()
        value = int(value_str)

        if value <= 0:
            return ScheduleValidationResponse(valid=False, error="時間間隔必須大於0")

        return ScheduleValidationResponse(
            valid=True,
            type=ScheduleType.RATE,
            description=f"每{value}{unit}執行一次",
            next_runs=self._calculate_next_runs_rate(value, unit)
        )
    
    async def get_schedule_templates(self) -> List[ScheduleTemplateResponse]:
        """獲取排程模板"""
        templates = [
            # 常用間隔
            {"name": "每分鐘", "expression": "rate(1 minute)", "category": "常用間隔", "description": "每分鐘執行一次"},
            {"name": "每5分鐘", "expression": "rate(5 minutes)", "category": "常用間隔", "description": "每5分鐘執行一次"},
            {"name": "每15分鐘", "expression": "rate(15 minutes)", "category": "常用間隔", "description": "每15分鐘執行一次"},
            {"name": "每30分鐘", "expression": "rate(30 minutes)", "category": "常用間隔", "description": "每30分鐘執行一次"},
            {"name": "每小時", "expression": "rate(1 hour)", "category": "常用間隔", "description": "每小時執行一次"},
            {"name": "每天", "expression": "rate(1 day)", "category": "常用間隔", "description": "每天執行一次"},
            
            # 每日排程
            {"name": "每天午夜", "expression": "cron(0 0 * * *)", "category": "每日排程", "description": "每天午夜12點執行"},
            {"name": "每天早上9點", "expression": "cron(0 9 * * *)", "category": "每日排程", "description": "每天早上9點執行"},
            {"name": "每天下午6點", "expression": "cron(0 18 * * *)", "category": "每日排程", "description": "每天下午6點執行"},
            
            # 工作日排程
            {"name": "工作日早上8點", "expression": "cron(0 8 * * 1-5)", "category": "工作日排程", "description": "週一到週五早上8點執行"},
            {"name": "工作日下午5點", "expression": "cron(0 17 * * 1-5)", "category": "工作日排程", "description": "週一到週五下午5點執行"},
            {"name": "工作日每小時", "expression": "cron(0 * * * 1-5)", "category": "工作日排程", "description": "工作日每小時執行"},
            
            # 週末排程
            {"name": "週六早上10點", "expression": "cron(0 10 * * 6)", "category": "週末排程", "description": "每週六早上10點執行"},
            {"name": "週日凌晨2點", "expression": "cron(0 2 * * 0)", "category": "週末排程", "description": "每週日凌晨2點執行"},
            
            # 每月排程
            {"name": "每月1號", "expression": "cron(0 0 1 * *)", "category": "每月排程", "description": "每月1號午夜執行"},
            {"name": "每月15號", "expression": "cron(0 0 15 * *)", "category": "每月排程", "description": "每月15號午夜執行"},
            {"name": "每月最後一天", "expression": "cron(0 0 L * *)", "category": "每月排程", "description": "每月最後一天午夜執行"},
        ]
        
        return [
            ScheduleTemplateResponse(
                name=t["name"],
                expression=t["expression"],
                category=t["category"],
                description=t["description"],
                type=ScheduleType.CRON if t["expression"].startswith("cron") else ScheduleType.RATE
            )
            for t in templates
        ]
    
    async def get_cron_help(self) -> List[CronHelpResponse]:
        """獲取 Cron 幫助信息"""
        return [
            CronHelpResponse(
                field=CronField.MINUTE,
                description="分鐘",
                range="0-59",
                special_chars=["*", ",", "-", "/"],
                examples=[
                    {"value": "*", "description": "每分鐘"},
                    {"value": "0", "description": "第0分鐘"},
                    {"value": "*/5", "description": "每5分鐘"},
                    {"value": "0,30", "description": "第0分和第30分"}
                ]
            ),
            CronHelpResponse(
                field=CronField.HOUR,
                description="小時",
                range="0-23",
                special_chars=["*", ",", "-", "/"],
                examples=[
                    {"value": "*", "description": "每小時"},
                    {"value": "9", "description": "早上9點"},
                    {"value": "*/2", "description": "每2小時"},
                    {"value": "9-17", "description": "9點到17點"}
                ]
            ),
            CronHelpResponse(
                field=CronField.DAY,
                description="日期",
                range="1-31",
                special_chars=["*", ",", "-", "/", "L", "W"],
                examples=[
                    {"value": "*", "description": "每天"},
                    {"value": "1", "description": "每月1號"},
                    {"value": "L", "description": "每月最後一天"},
                    {"value": "1,15", "description": "每月1號和15號"}
                ]
            ),
            CronHelpResponse(
                field=CronField.MONTH,
                description="月份",
                range="1-12",
                special_chars=["*", ",", "-", "/"],
                examples=[
                    {"value": "*", "description": "每月"},
                    {"value": "1", "description": "1月"},
                    {"value": "1,7", "description": "1月和7月"},
                    {"value": "3-6", "description": "3月到6月"}
                ]
            ),
            CronHelpResponse(
                field=CronField.WEEKDAY,
                description="星期",
                range="0-7 (0和7都是週日)",
                special_chars=["*", ",", "-", "/", "L", "#"],
                examples=[
                    {"value": "*", "description": "每天"},
                    {"value": "1", "description": "週一"},
                    {"value": "1-5", "description": "週一到週五"},
                    {"value": "0,6", "description": "週末"}
                ]
            )
        ]
    
    def _calculate_next_runs_rate(self, value: int, unit: str, count: int = 5) -> List[str]:
        """計算 Rate 表達式的接下來執行時間"""
        now = datetime.now(tz=self.tz)
        next_runs = []
        if unit.startswith('second'):
            delta = timedelta(seconds=value)
        elif unit.startswith('minute'):
            delta = timedelta(minutes=value)
        elif unit.startswith('hour'):
            delta = timedelta(hours=value)
        elif unit.startswith('day'):
            delta = timedelta(days=value)
        else:
            return []
        
        current = now + delta
        for _ in range(count):
            next_runs.append(current.strftime("%Y-%m-%d %H:%M:%S"))
            current += delta
        
        return next_runs
    
    def _calculate_next_runs_cron(self, expression: str, count: int = 5) -> List[str]:
        """簡化版：根據 cron 表達式產生下幾次執行時間（不使用 croniter）"""
        try:
            # 例如：cron(0 9 * * 1-5)
            expr = expression[5:-1].strip()
            minute, hour, day, month, weekday = expr.split()

            now = datetime.now()
            next_runs = []

            # 僅處理最常見型態：「每天固定時刻」或「每週特定日」
            for _ in range(count):
                next_time = now.replace(second=0, microsecond=0)

                # 固定時間
                next_time = next_time.replace(hour=int(hour), minute=int(minute))

                # 若已過當日時間 → +1 天
                if next_time <= now:
                    next_time += timedelta(days=1)

                # 若有 weekday 限制（0=週一，6=週日）
                if weekday != "*":
                    valid_days = []
                    for part in weekday.split(','):
                        if '-' in part:
                            a, b = part.split('-')
                            valid_days.extend(range(int(a), int(b)+1))
                        else:
                            valid_days.append(int(part))

                    while next_time.weekday() + 1 not in valid_days:
                        next_time += timedelta(days=1)

                next_runs.append(next_time.strftime("%Y-%m-%d %H:%M:%S"))
                now = next_time + timedelta(seconds=1)

            return next_runs

        except Exception as e:
            logger.error(f"Error parsing cron '{expression}': {e}")
            return []
    
    def _calculate_next_runs_from_expression(self, expression: str) -> List[str]:
        """從表達式計算接下來的執行時間"""
        if expression.startswith('cron('):
            return self._calculate_next_runs_cron(expression)
        elif expression.startswith('rate('):
            rate_expr = expression[5:-1]
            match = re.match(r'(\d+)\s+(minute|minutes|hour|hours|day|days)', rate_expr)
            if match:
                value, unit = match.groups()
                return self._calculate_next_runs_rate(int(value), unit)
        return []
    
    def _generate_cron_description(self, request: CronExpressionRequest) -> str:
        """生成 Cron 表達式描述"""
        parts = [request.minute, request.hour, request.day, request.month, request.weekday]
        return self._generate_cron_description_from_parts(parts)
    
    def _generate_cron_description_from_parts(self, parts: List[str]) -> str:
        """從 Cron 部分生成描述"""
        minute, hour, day, month, weekday = parts
        
        desc_parts = []
        
        # 分析頻率
        if minute == "*" and hour == "*" and day == "*" and month == "*" and weekday == "*":
            return "每分鐘執行"
        
        if minute != "*" and hour == "*":
            desc_parts.append(f"每小時第{minute}分鐘")
        elif minute == "*" and hour != "*":
            desc_parts.append(f"每天{hour}點的每分鐘")
        elif minute != "*" and hour != "*":
            desc_parts.append(f"每天{hour}:{minute.zfill(2)}")
        
        if weekday != "*":
            weekday_map = {"0": "週日", "1": "週一", "2": "週二", "3": "週三", "4": "週四", "5": "週五", "6": "週六"}
            if "-" in weekday:
                start, end = weekday.split("-")
                desc_parts.append(f"{weekday_map.get(start, start)}到{weekday_map.get(end, end)}")
            elif "," in weekday:
                days = [weekday_map.get(d, d) for d in weekday.split(",")]
                desc_parts.append(",".join(days))
            else:
                desc_parts.append(weekday_map.get(weekday, weekday))
        
        if day != "*":
            if day == "L":
                desc_parts.append("每月最後一天")
            else:
                desc_parts.append(f"每月{day}號")
        
        if month != "*":
            desc_parts.append(f"{month}月")
        
        return " ".join(desc_parts) if desc_parts else "自定義排程"