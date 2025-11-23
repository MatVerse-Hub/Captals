import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import {
  Filter,
  Download,
  TrendingUp,
  BarChart3,
  PieChart,
  Grid3x3,
  List,
  SlidersHorizontal,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  X
} from 'lucide-react';

// Base44 API Configuration
const BASE44_CONFIG = {
  apiKey: '431d90fd5dc046bea66c70686ed2a343',
  appId: '69224f836e8f58657363c48f',
  baseUrl: 'https://api.base44.com',
  entityName: 'MatVerseOS'
};

const Base44FilterableDashboard = () => {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  // Filters
  const [filters, setFilters] = useState({
    search: '',
    status: 'all',
    omegaScoreMin: 0,
    omegaScoreMax: 1,
    dateFrom: '',
    dateTo: '',
    metadataType: 'all'
  });

  // Sorting
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  // Active filters count
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (filters.search) count++;
    if (filters.status !== 'all') count++;
    if (filters.omegaScoreMin > 0 || filters.omegaScoreMax < 1) count++;
    if (filters.dateFrom || filters.dateTo) count++;
    if (filters.metadataType !== 'all') count++;
    return count;
  }, [filters]);

  // Mock data (replace with actual Base44 API call)
  useEffect(() => {
    const mockEntities = [
      {
        id: '1',
        name: 'MatVerseOS Core',
        description: 'Main operating system kernel',
        omega_score: 0.87,
        status: 'active',
        created_at: '2025-01-15T10:00:00Z',
        metadata: { version: '1.0.0', type: 'system', category: 'core' }
      },
      {
        id: '2',
        name: 'Dual-Brain Sync',
        description: 'TeraBox + GDrive synchronization service',
        omega_score: 0.92,
        status: 'active',
        created_at: '2025-01-16T14:30:00Z',
        metadata: { version: '1.1.0', type: 'service', category: 'storage' }
      },
      {
        id: '3',
        name: 'IA-MetaMask Agent',
        description: 'Autonomous wallet operations',
        omega_score: 0.78,
        status: 'pending',
        created_at: '2025-01-17T09:15:00Z',
        metadata: { version: '0.9.0', type: 'agent', category: 'blockchain' }
      },
      {
        id: '4',
        name: 'LUA-AutoHeal Security',
        description: '8-layer antifragile security system',
        omega_score: 0.95,
        status: 'active',
        created_at: '2025-01-18T11:20:00Z',
        metadata: { version: '2.0.0', type: 'system', category: 'security' }
      },
      {
        id: '5',
        name: 'Ω-GATE Governance',
        description: 'Mathematical governance protocol',
        omega_score: 0.65,
        status: 'error',
        created_at: '2025-01-19T16:45:00Z',
        metadata: { version: '0.5.0', type: 'service', category: 'governance' }
      },
      {
        id: '6',
        name: 'ClaudeCode-TURBO',
        description: 'Optimized Claude Code fork',
        omega_score: 0.88,
        status: 'active',
        created_at: '2025-01-20T08:00:00Z',
        metadata: { version: '1.2.0', type: 'agent', category: 'ai' }
      }
    ];
    setEntities(mockEntities);
  }, []);

  // Filtered and sorted entities
  const filteredEntities = useMemo(() => {
    let result = [...entities];

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      result = result.filter(e =>
        e.name.toLowerCase().includes(searchLower) ||
        e.description.toLowerCase().includes(searchLower)
      );
    }

    // Status filter
    if (filters.status !== 'all') {
      result = result.filter(e => e.status === filters.status);
    }

    // Omega score filter
    result = result.filter(e =>
      e.omega_score >= filters.omegaScoreMin &&
      e.omega_score <= filters.omegaScoreMax
    );

    // Date filter
    if (filters.dateFrom) {
      result = result.filter(e => new Date(e.created_at) >= new Date(filters.dateFrom));
    }
    if (filters.dateTo) {
      result = result.filter(e => new Date(e.created_at) <= new Date(filters.dateTo));
    }

    // Metadata type filter
    if (filters.metadataType !== 'all') {
      result = result.filter(e => e.metadata?.type === filters.metadataType);
    }

    // Sorting
    result.sort((a, b) => {
      let aVal, bVal;

      switch (sortBy) {
        case 'name':
          aVal = a.name;
          bVal = b.name;
          break;
        case 'omega_score':
          aVal = a.omega_score;
          bVal = b.omega_score;
          break;
        case 'created_at':
        default:
          aVal = new Date(a.created_at);
          bVal = new Date(b.created_at);
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    return result;
  }, [entities, filters, sortBy, sortOrder]);

  // Statistics
  const stats = useMemo(() => {
    return {
      total: entities.length,
      active: entities.filter(e => e.status === 'active').length,
      pending: entities.filter(e => e.status === 'pending').length,
      error: entities.filter(e => e.status === 'error').length,
      avgOmegaScore: entities.length > 0
        ? entities.reduce((sum, e) => sum + e.omega_score, 0) / entities.length
        : 0,
      highPerformance: entities.filter(e => e.omega_score >= 0.8).length
    };
  }, [entities]);

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      search: '',
      status: 'all',
      omegaScoreMin: 0,
      omegaScoreMax: 1,
      dateFrom: '',
      dateTo: '',
      metadataType: 'all'
    });
    toast.success('Filters cleared');
  };

  // Export data
  const exportData = () => {
    const csvContent = [
      ['Name', 'Description', 'Ω-Score', 'Status', 'Created', 'Type'],
      ...filteredEntities.map(e => [
        e.name,
        e.description,
        e.omega_score,
        e.status,
        new Date(e.created_at).toLocaleDateString(),
        e.metadata?.type || 'N/A'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `matverse-entities-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    toast.success('Data exported successfully');
  };

  // Get status badge
  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { icon: CheckCircle, variant: 'default', color: 'text-green-500' },
      pending: { icon: Clock, variant: 'secondary', color: 'text-yellow-500' },
      error: { icon: XCircle, variant: 'destructive', color: 'text-red-500' }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className={`h-3 w-3 ${config.color}`} />
        {status}
      </Badge>
    );
  };

  // Get Ω-score badge
  const getOmegaScoreBadge = (score) => {
    const color = score >= 0.8 ? 'bg-green-500' : score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500';
    return (
      <Badge className={`${color} text-white`}>
        Ω {score.toFixed(2)}
      </Badge>
    );
  };

  return (
    <div className="w-full space-y-4">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="text-sm text-slate-400 mb-1">Total</div>
            <div className="text-2xl font-bold text-white">{stats.total}</div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="text-sm text-slate-400 mb-1">Active</div>
            <div className="text-2xl font-bold text-green-500">{stats.active}</div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="text-sm text-slate-400 mb-1">Pending</div>
            <div className="text-2xl font-bold text-yellow-500">{stats.pending}</div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="text-sm text-slate-400 mb-1">Error</div>
            <div className="text-2xl font-bold text-red-500">{stats.error}</div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="text-sm text-slate-400 mb-1">Avg Ω</div>
            <div className="text-2xl font-bold text-purple-500">
              {stats.avgOmegaScore.toFixed(2)}
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="text-sm text-slate-400 mb-1">High Perf</div>
            <div className="text-2xl font-bold text-blue-500">{stats.highPerformance}</div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-white">
                <Filter className="h-5 w-5" />
                Filterable Dashboard
              </CardTitle>
              <CardDescription>
                Advanced filtering and analytics for Base44 entities
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              >
                {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid3x3 className="h-4 w-4" />}
              </Button>
              <Button variant="outline" size="sm" onClick={exportData}>
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="filters" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-slate-800">
              <TabsTrigger value="filters">
                <SlidersHorizontal className="h-4 w-4 mr-2" />
                Filters
                {activeFiltersCount > 0 && (
                  <Badge variant="destructive" className="ml-2">{activeFiltersCount}</Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="data">
                <BarChart3 className="h-4 w-4 mr-2" />
                Data ({filteredEntities.length})
              </TabsTrigger>
              <TabsTrigger value="charts">
                <PieChart className="h-4 w-4 mr-2" />
                Analytics
              </TabsTrigger>
            </TabsList>

            {/* Filters Tab */}
            <TabsContent value="filters" className="space-y-4 mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Search */}
                <div>
                  <Label>Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search entities..."
                      value={filters.search}
                      onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                      className="bg-slate-800 border-slate-700 pl-9"
                    />
                  </div>
                </div>

                {/* Status */}
                <div>
                  <Label>Status</Label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                    className="w-full h-10 px-3 rounded-md bg-slate-800 border border-slate-700 text-white"
                  >
                    <option value="all">All Statuses</option>
                    <option value="active">Active</option>
                    <option value="pending">Pending</option>
                    <option value="error">Error</option>
                  </select>
                </div>

                {/* Metadata Type */}
                <div>
                  <Label>Type</Label>
                  <select
                    value={filters.metadataType}
                    onChange={(e) => setFilters({ ...filters, metadataType: e.target.value })}
                    className="w-full h-10 px-3 rounded-md bg-slate-800 border border-slate-700 text-white"
                  >
                    <option value="all">All Types</option>
                    <option value="system">System</option>
                    <option value="service">Service</option>
                    <option value="agent">Agent</option>
                  </select>
                </div>

                {/* Omega Score Range */}
                <div>
                  <Label>Ω-Score Min ({filters.omegaScoreMin.toFixed(2)})</Label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={filters.omegaScoreMin}
                    onChange={(e) => setFilters({ ...filters, omegaScoreMin: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>

                <div>
                  <Label>Ω-Score Max ({filters.omegaScoreMax.toFixed(2)})</Label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={filters.omegaScoreMax}
                    onChange={(e) => setFilters({ ...filters, omegaScoreMax: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>

                {/* Date Range */}
                <div>
                  <Label>Date From</Label>
                  <Input
                    type="date"
                    value={filters.dateFrom}
                    onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                    className="bg-slate-800 border-slate-700"
                  />
                </div>

                <div>
                  <Label>Date To</Label>
                  <Input
                    type="date"
                    value={filters.dateTo}
                    onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                    className="bg-slate-800 border-slate-700"
                  />
                </div>

                {/* Sort By */}
                <div>
                  <Label>Sort By</Label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full h-10 px-3 rounded-md bg-slate-800 border border-slate-700 text-white"
                  >
                    <option value="created_at">Created Date</option>
                    <option value="name">Name</option>
                    <option value="omega_score">Ω-Score</option>
                  </select>
                </div>

                <div>
                  <Label>Sort Order</Label>
                  <select
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value)}
                    className="w-full h-10 px-3 rounded-md bg-slate-800 border border-slate-700 text-white"
                  >
                    <option value="desc">Descending</option>
                    <option value="asc">Ascending</option>
                  </select>
                </div>
              </div>

              {activeFiltersCount > 0 && (
                <Button variant="outline" onClick={clearFilters} className="w-full">
                  <X className="h-4 w-4 mr-2" />
                  Clear All Filters ({activeFiltersCount})
                </Button>
              )}
            </TabsContent>

            {/* Data Tab */}
            <TabsContent value="data" className="mt-4">
              {viewMode === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredEntities.map((entity) => (
                    <Card key={entity.id} className="bg-slate-800 border-slate-700">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-white text-lg">
                            {entity.name}
                          </CardTitle>
                          {getOmegaScoreBadge(entity.omega_score)}
                        </div>
                        <CardDescription>{entity.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-400">Status:</span>
                            {getStatusBadge(entity.status)}
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-400">Type:</span>
                            <Badge variant="outline">{entity.metadata?.type}</Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-400">Created:</span>
                            <span className="text-sm text-white">
                              {new Date(entity.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredEntities.map((entity) => (
                    <div
                      key={entity.id}
                      className="p-4 bg-slate-800 border border-slate-700 rounded-lg flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <div className="font-medium text-white">{entity.name}</div>
                        <div className="text-sm text-slate-400">{entity.description}</div>
                      </div>
                      <div className="flex items-center gap-4">
                        {getOmegaScoreBadge(entity.omega_score)}
                        {getStatusBadge(entity.status)}
                        <Badge variant="outline">{entity.metadata?.type}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {filteredEntities.length === 0 && (
                <div className="text-center py-12 text-slate-400">
                  No entities match your filters. Try adjusting the criteria.
                </div>
              )}
            </TabsContent>

            {/* Analytics Tab */}
            <TabsContent value="charts" className="mt-4">
              <div className="space-y-6">
                {/* Status Distribution */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Status Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-slate-300">Active</span>
                          <span className="text-sm font-bold text-green-500">{stats.active}</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${(stats.active / stats.total) * 100}%` }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-slate-300">Pending</span>
                          <span className="text-sm font-bold text-yellow-500">{stats.pending}</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-yellow-500 h-2 rounded-full"
                            style={{ width: `${(stats.pending / stats.total) * 100}%` }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-slate-300">Error</span>
                          <span className="text-sm font-bold text-red-500">{stats.error}</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-red-500 h-2 rounded-full"
                            style={{ width: `${(stats.error / stats.total) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Performance Metrics */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      Performance Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-slate-900 rounded-lg">
                        <div className="text-3xl font-bold text-purple-500">
                          Ω {stats.avgOmegaScore.toFixed(3)}
                        </div>
                        <div className="text-sm text-slate-400 mt-1">Average Ω-Score</div>
                      </div>
                      <div className="text-center p-4 bg-slate-900 rounded-lg">
                        <div className="text-3xl font-bold text-blue-500">
                          {((stats.highPerformance / stats.total) * 100).toFixed(0)}%
                        </div>
                        <div className="text-sm text-slate-400 mt-1">High Performance</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default Base44FilterableDashboard;
