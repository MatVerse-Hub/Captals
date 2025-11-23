import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import {
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Loader2,
  Play,
  Pause,
  Trash2,
  FileText,
  GitBranch,
  Zap
} from 'lucide-react';

// Base44 API Configuration
const BASE44_CONFIG = {
  apiKey: '431d90fd5dc046bea66c70686ed2a343',
  appId: '69224f836e8f58657363c48f',
  baseUrl: 'https://api.base44.com',
  entityName: 'MatVerseOS'
};

// Operation types
const OPERATION_TYPES = {
  CREATE: { label: 'Create', icon: Play, color: 'text-green-500' },
  READ: { label: 'Read', icon: FileText, color: 'text-blue-500' },
  UPDATE: { label: 'Update', icon: RefreshCw, color: 'text-yellow-500' },
  DELETE: { label: 'Delete', icon: Trash2, color: 'text-red-500' },
  SYNC: { label: 'Sync', icon: GitBranch, color: 'text-purple-500' },
  BATCH: { label: 'Batch', icon: Zap, color: 'text-orange-500' }
};

const Base44StatusTracker = () => {
  const [operations, setOperations] = useState([]);
  const [isTracking, setIsTracking] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'success', 'failed', 'pending'

  const operationIdRef = useRef(1);

  // Statistics
  const stats = React.useMemo(() => {
    const total = operations.length;
    const success = operations.filter(op => op.status === 'success').length;
    const failed = operations.filter(op => op.status === 'failed').length;
    const pending = operations.filter(op => op.status === 'pending').length;
    const inProgress = operations.filter(op => op.status === 'in_progress').length;

    // Calculate average duration for completed operations
    const completedOps = operations.filter(op => op.status === 'success' || op.status === 'failed');
    const avgDuration = completedOps.length > 0
      ? completedOps.reduce((sum, op) => sum + (op.duration || 0), 0) / completedOps.length
      : 0;

    // Calculate success rate
    const successRate = total > 0 ? (success / total) * 100 : 0;

    return {
      total,
      success,
      failed,
      pending,
      inProgress,
      avgDuration,
      successRate
    };
  }, [operations]);

  // Filtered operations
  const filteredOperations = React.useMemo(() => {
    if (filter === 'all') return operations;
    return operations.filter(op => op.status === filter);
  }, [operations, filter]);

  // Add new operation
  const addOperation = (type, entityName, metadata = {}) => {
    const newOp = {
      id: operationIdRef.current++,
      type,
      entityName,
      status: 'pending',
      startTime: Date.now(),
      metadata,
      logs: []
    };

    setOperations(prev => [newOp, ...prev]);
    return newOp.id;
  };

  // Update operation status
  const updateOperation = (id, updates) => {
    setOperations(prev => prev.map(op => {
      if (op.id === id) {
        const updatedOp = { ...op, ...updates };

        // Calculate duration if completed
        if ((updates.status === 'success' || updates.status === 'failed') && !updatedOp.duration) {
          updatedOp.duration = Date.now() - op.startTime;
          updatedOp.endTime = Date.now();
        }

        return updatedOp;
      }
      return op;
    }));
  };

  // Add log to operation
  const addOperationLog = (id, message, level = 'info') => {
    setOperations(prev => prev.map(op => {
      if (op.id === id) {
        return {
          ...op,
          logs: [
            ...op.logs,
            {
              timestamp: Date.now(),
              message,
              level
            }
          ]
        };
      }
      return op;
    }));
  };

  // Simulate operation execution
  const executeOperation = async (opId, type, entityName) => {
    updateOperation(opId, { status: 'in_progress' });
    addOperationLog(opId, `Starting ${type.toLowerCase()} operation for ${entityName}`, 'info');

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 500));

    // Random success/failure (90% success rate)
    const success = Math.random() > 0.1;

    if (success) {
      addOperationLog(opId, `${type} operation completed successfully`, 'success');
      updateOperation(opId, { status: 'success' });
      toast.success(`${type} operation completed`);
    } else {
      addOperationLog(opId, `${type} operation failed: Network timeout`, 'error');
      updateOperation(opId, { status: 'failed', error: 'Network timeout' });
      toast.error(`${type} operation failed`);
    }
  };

  // Retry failed operation
  const retryOperation = async (operation) => {
    const newOpId = addOperation(operation.type, operation.entityName, operation.metadata);
    await executeOperation(newOpId, operation.type, operation.entityName);
  };

  // Simulate random operations for demo
  useEffect(() => {
    if (!isTracking) return;

    const interval = setInterval(() => {
      const types = Object.keys(OPERATION_TYPES);
      const type = types[Math.floor(Math.random() * types.length)];
      const entities = [
        'MatVerseOS Core',
        'Dual-Brain Sync',
        'IA-MetaMask Agent',
        'LUA-AutoHeal',
        'Ω-GATE',
        'ClaudeCode-TURBO'
      ];
      const entityName = entities[Math.floor(Math.random() * entities.length)];

      const opId = addOperation(type, entityName);
      executeOperation(opId, type, entityName);
    }, Math.random() * 5000 + 2000);

    return () => clearInterval(interval);
  }, [isTracking]);

  // Clear all operations
  const clearOperations = () => {
    setOperations([]);
    toast.success('Operations cleared');
  };

  // Get status badge
  const getStatusBadge = (status) => {
    const statusConfig = {
      success: { icon: CheckCircle, variant: 'default', color: 'text-green-500', bg: 'bg-green-950/30' },
      failed: { icon: XCircle, variant: 'destructive', color: 'text-red-500', bg: 'bg-red-950/30' },
      pending: { icon: Clock, variant: 'secondary', color: 'text-slate-500', bg: 'bg-slate-950/30' },
      in_progress: { icon: Loader2, variant: 'default', color: 'text-blue-500', bg: 'bg-blue-950/30', spin: true }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className={`h-3 w-3 ${config.color} ${config.spin ? 'animate-spin' : ''}`} />
        {status.replace('_', ' ')}
      </Badge>
    );
  };

  // Format duration
  const formatDuration = (ms) => {
    if (!ms) return '-';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="w-full space-y-4">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Total Ops</span>
              <Activity className="h-4 w-4 text-blue-500" />
            </div>
            <div className="text-2xl font-bold text-white">{stats.total}</div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Success Rate</span>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-500">
              {stats.successRate.toFixed(0)}%
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Avg Duration</span>
              <Clock className="h-4 w-4 text-purple-500" />
            </div>
            <div className="text-2xl font-bold text-purple-500">
              {formatDuration(stats.avgDuration)}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">In Progress</span>
              <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
            </div>
            <div className="text-2xl font-bold text-blue-500">
              {stats.inProgress}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tracker */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-white">
                <Activity className="h-5 w-5" />
                Operation Status Tracker
              </CardTitle>
              <CardDescription>
                Real-time monitoring of all Base44 API operations
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={isTracking ? 'destructive' : 'default'}
                size="sm"
                onClick={() => setIsTracking(!isTracking)}
              >
                {isTracking ? (
                  <>
                    <Pause className="h-4 w-4 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Resume
                  </>
                )}
              </Button>
              <Button variant="outline" size="sm" onClick={clearOperations}>
                <Trash2 className="h-4 w-4 mr-2" />
                Clear
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="operations" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-slate-800">
              <TabsTrigger value="operations">
                Operations ({operations.length})
              </TabsTrigger>
              <TabsTrigger value="stats">
                <BarChart3 className="h-4 w-4 mr-2" />
                Statistics
              </TabsTrigger>
              <TabsTrigger value="logs">
                <FileText className="h-4 w-4 mr-2" />
                Detailed Logs
              </TabsTrigger>
            </TabsList>

            {/* Operations Tab */}
            <TabsContent value="operations" className="space-y-4 mt-4">
              {/* Filter */}
              <div className="flex items-center gap-2">
                <Button
                  variant={filter === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('all')}
                >
                  All ({stats.total})
                </Button>
                <Button
                  variant={filter === 'success' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('success')}
                >
                  Success ({stats.success})
                </Button>
                <Button
                  variant={filter === 'failed' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('failed')}
                >
                  Failed ({stats.failed})
                </Button>
                <Button
                  variant={filter === 'in_progress' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('in_progress')}
                >
                  In Progress ({stats.inProgress})
                </Button>
              </div>

              {/* Operations List */}
              <ScrollArea className="h-[500px] rounded-md border border-slate-800 bg-slate-950">
                <div className="p-4 space-y-2">
                  {filteredOperations.length === 0 ? (
                    <div className="text-center py-12 text-slate-400">
                      No operations to display. {isTracking ? 'Waiting for operations...' : 'Tracking is paused.'}
                    </div>
                  ) : (
                    filteredOperations.map((operation) => {
                      const opConfig = OPERATION_TYPES[operation.type];
                      const Icon = opConfig.icon;

                      return (
                        <Card
                          key={operation.id}
                          className={`${
                            operation.status === 'failed'
                              ? 'bg-red-950/20 border-red-900/50'
                              : operation.status === 'success'
                              ? 'bg-green-950/20 border-green-900/50'
                              : 'bg-slate-800 border-slate-700'
                          }`}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-3">
                                <Icon className={`h-5 w-5 ${opConfig.color}`} />
                                <div>
                                  <div className="font-medium text-white">
                                    {opConfig.label}: {operation.entityName}
                                  </div>
                                  <div className="text-xs text-slate-400">
                                    Started: {formatTime(operation.startTime)}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                {getStatusBadge(operation.status)}
                                {operation.status === 'failed' && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => retryOperation(operation)}
                                  >
                                    <RefreshCw className="h-3 w-3 mr-1" />
                                    Retry
                                  </Button>
                                )}
                              </div>
                            </div>

                            {/* Progress bar for in-progress operations */}
                            {operation.status === 'in_progress' && (
                              <div className="mb-2">
                                <Progress value={50} className="h-1" />
                              </div>
                            )}

                            {/* Duration and error */}
                            <div className="flex items-center justify-between text-xs">
                              <div className="text-slate-400">
                                Duration: {formatDuration(operation.duration)}
                              </div>
                              {operation.error && (
                                <div className="text-red-400 flex items-center gap-1">
                                  <AlertTriangle className="h-3 w-3" />
                                  {operation.error}
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Statistics Tab */}
            <TabsContent value="stats" className="space-y-4 mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Status Distribution */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white text-sm">Status Distribution</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-slate-300">Success</span>
                        <span className="text-sm font-bold text-green-500">{stats.success}</span>
                      </div>
                      <Progress
                        value={stats.total > 0 ? (stats.success / stats.total) * 100 : 0}
                        className="h-2 bg-slate-700"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-slate-300">Failed</span>
                        <span className="text-sm font-bold text-red-500">{stats.failed}</span>
                      </div>
                      <Progress
                        value={stats.total > 0 ? (stats.failed / stats.total) * 100 : 0}
                        className="h-2 bg-slate-700"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-slate-300">In Progress</span>
                        <span className="text-sm font-bold text-blue-500">{stats.inProgress}</span>
                      </div>
                      <Progress
                        value={stats.total > 0 ? (stats.inProgress / stats.total) * 100 : 0}
                        className="h-2 bg-slate-700"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Operation Types */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white text-sm">Operation Types</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(OPERATION_TYPES).map(([key, config]) => {
                        const count = operations.filter(op => op.type === key).length;
                        const Icon = config.icon;

                        return (
                          <div key={key} className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Icon className={`h-4 w-4 ${config.color}`} />
                              <span className="text-sm text-slate-300">{config.label}</span>
                            </div>
                            <Badge variant="outline">{count}</Badge>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Logs Tab */}
            <TabsContent value="logs" className="mt-4">
              <ScrollArea className="h-[500px] rounded-md border border-slate-800 bg-slate-950">
                <div className="p-4 space-y-4">
                  {operations.filter(op => op.logs.length > 0).map((operation) => (
                    <div key={operation.id} className="space-y-2">
                      <div className="font-medium text-white flex items-center gap-2">
                        <Badge variant="outline">#{operation.id}</Badge>
                        {operation.entityName}
                      </div>
                      <div className="pl-4 space-y-1">
                        {operation.logs.map((log, idx) => (
                          <div
                            key={idx}
                            className={`text-sm flex items-start gap-2 ${
                              log.level === 'error'
                                ? 'text-red-400'
                                : log.level === 'success'
                                ? 'text-green-400'
                                : 'text-slate-400'
                            }`}
                          >
                            <span className="text-xs text-slate-500">
                              {formatTime(log.timestamp)}
                            </span>
                            <span>{log.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default Base44StatusTracker;
