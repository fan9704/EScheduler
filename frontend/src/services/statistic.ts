import { apiService } from './api';

import { StatisticDashboardMetricResponse } from '@/models/statistic';

class StatisticService {
  private readonly basePath = '/statistic';
  async get_dashboard_statistic(): Promise<StatisticDashboardMetricResponse> {
    return await apiService.get<StatisticDashboardMetricResponse>(
      `${this.basePath}/dashboard-metrics`,
    );
  }
}

export const statisticService = new StatisticService();
export default statisticService;
