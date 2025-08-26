import { StatisticDashboardMetricResponse } from "@/models/statistic";
import { apiService } from "./api";

class StatisticService{
    private readonly basePath = '/statistic'
    async get_dashboard_statistic(): Promise<StatisticDashboardMetricResponse>{
        const response = await apiService.get<StatisticDashboardMetricResponse>(`${this.basePath}/dashboard-metrics`)
        return response
    }
}
    
export const statisticService = new StatisticService()
export default statisticService