import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import {
  Database,
  Plus,
  Edit,
  Trash2,
  Search,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  Loader2
} from 'lucide-react';

// Base44 API Configuration
const BASE44_CONFIG = {
  apiKey: '431d90fd5dc046bea66c70686ed2a343',
  appId: '69224f836e8f58657363c48f',
  baseUrl: 'https://api.base44.com',
  entityName: 'MatVerseOS'
};

const Base44EntityManager = () => {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingEntity, setEditingEntity] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    omega_score: 0,
    status: 'pending',
    metadata: '{}'
  });

  // Fetch entities from Base44 API
  const fetchEntities = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BASE44_CONFIG.baseUrl}/api/apps/${BASE44_CONFIG.appId}/entities/${BASE44_CONFIG.entityName}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setEntities(data.entities || []);
      toast.success(`Loaded ${data.entities?.length || 0} entities`);
    } catch (error) {
      console.error('Error fetching entities:', error);
      toast.error(`Failed to fetch entities: ${error.message}`);

      // Fallback to mock data for development
      setEntities([
        {
          id: '1',
          name: 'MatVerseOS Core',
          description: 'Main OS system',
          omega_score: 0.87,
          status: 'active',
          created_at: new Date().toISOString(),
          metadata: { version: '1.0.0', type: 'system' }
        },
        {
          id: '2',
          name: 'Dual-Brain Sync',
          description: 'TeraBox + GDrive synchronization',
          omega_score: 0.92,
          status: 'active',
          created_at: new Date().toISOString(),
          metadata: { version: '1.1.0', type: 'service' }
        },
        {
          id: '3',
          name: 'IA-MetaMask Agent',
          description: 'Autonomous wallet operations',
          omega_score: 0.78,
          status: 'pending',
          created_at: new Date().toISOString(),
          metadata: { version: '0.9.0', type: 'agent' }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Create or Update entity
  const saveEntity = async () => {
    setLoading(true);
    try {
      const method = editingEntity ? 'PUT' : 'POST';
      const url = editingEntity
        ? `${BASE44_CONFIG.baseUrl}/api/apps/${BASE44_CONFIG.appId}/entities/${BASE44_CONFIG.entityName}/${editingEntity.id}`
        : `${BASE44_CONFIG.baseUrl}/api/apps/${BASE44_CONFIG.appId}/entities/${BASE44_CONFIG.entityName}`;

      const payload = {
        ...formData,
        metadata: JSON.parse(formData.metadata),
        omega_score: parseFloat(formData.omega_score),
        updated_at: new Date().toISOString()
      };

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${BASE44_CONFIG.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      toast.success(editingEntity ? 'Entity updated!' : 'Entity created!');

      // Refresh entities list
      await fetchEntities();

      // Reset form
      setIsDialogOpen(false);
      setEditingEntity(null);
      setFormData({
        name: '',
        description: '',
        omega_score: 0,
        status: 'pending',
        metadata: '{}'
      });
    } catch (error) {
      console.error('Error saving entity:', error);
      toast.error(`Failed to save entity: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Delete entity
  const deleteEntity = async (entityId) => {
    if (!confirm('Are you sure you want to delete this entity?')) return;

    setLoading(true);
    try {
      const response = await fetch(
        `${BASE44_CONFIG.baseUrl}/api/apps/${BASE44_CONFIG.appId}/entities/${BASE44_CONFIG.entityName}/${entityId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      toast.success('Entity deleted!');
      await fetchEntities();
    } catch (error) {
      console.error('Error deleting entity:', error);
      toast.error(`Failed to delete entity: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Open edit dialog
  const openEditDialog = (entity) => {
    setEditingEntity(entity);
    setFormData({
      name: entity.name,
      description: entity.description,
      omega_score: entity.omega_score,
      status: entity.status,
      metadata: JSON.stringify(entity.metadata || {}, null, 2)
    });
    setIsDialogOpen(true);
  };

  // Open create dialog
  const openCreateDialog = () => {
    setEditingEntity(null);
    setFormData({
      name: '',
      description: '',
      omega_score: 0,
      status: 'pending',
      metadata: '{}'
    });
    setIsDialogOpen(true);
  };

  // Filter entities by search term
  const filteredEntities = entities.filter(entity =>
    entity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entity.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

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

  // Get Ω-score badge with color
  const getOmegaScoreBadge = (score) => {
    const color = score >= 0.8 ? 'bg-green-500' : score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500';
    return (
      <Badge className={`${color} text-white`}>
        Ω {score.toFixed(2)}
      </Badge>
    );
  };

  // Load entities on mount
  useEffect(() => {
    fetchEntities();
  }, []);

  return (
    <div className="w-full space-y-4">
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-white">
                <Database className="h-5 w-5" />
                Base44 Entity Manager
              </CardTitle>
              <CardDescription>
                Manage MatVerseOS entities with full CRUD operations
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={fetchEntities}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button onClick={openCreateDialog}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Entity
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-900 border-slate-800 text-white">
                  <DialogHeader>
                    <DialogTitle>
                      {editingEntity ? 'Edit Entity' : 'Create New Entity'}
                    </DialogTitle>
                    <DialogDescription>
                      {editingEntity ? 'Update entity details' : 'Add a new entity to Base44'}
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="name">Name</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="Entity name"
                        className="bg-slate-800 border-slate-700"
                      />
                    </div>
                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        placeholder="Entity description"
                        className="bg-slate-800 border-slate-700"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="omega_score">Ω-Score (0-1)</Label>
                        <Input
                          id="omega_score"
                          type="number"
                          step="0.01"
                          min="0"
                          max="1"
                          value={formData.omega_score}
                          onChange={(e) => setFormData({ ...formData, omega_score: e.target.value })}
                          className="bg-slate-800 border-slate-700"
                        />
                      </div>
                      <div>
                        <Label htmlFor="status">Status</Label>
                        <select
                          id="status"
                          value={formData.status}
                          onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                          className="w-full h-10 px-3 rounded-md bg-slate-800 border border-slate-700 text-white"
                        >
                          <option value="pending">Pending</option>
                          <option value="active">Active</option>
                          <option value="error">Error</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="metadata">Metadata (JSON)</Label>
                      <Textarea
                        id="metadata"
                        value={formData.metadata}
                        onChange={(e) => setFormData({ ...formData, metadata: e.target.value })}
                        placeholder='{"key": "value"}'
                        className="bg-slate-800 border-slate-700 font-mono text-sm"
                        rows={4}
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        onClick={() => setIsDialogOpen(false)}
                      >
                        Cancel
                      </Button>
                      <Button onClick={saveEntity} disabled={loading}>
                        {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                        {editingEntity ? 'Update' : 'Create'}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Search */}
            <div className="flex items-center gap-2">
              <Search className="h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search entities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-slate-800 border-slate-700"
              />
            </div>

            {/* Entities Table */}
            {loading && entities.length === 0 ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
              </div>
            ) : (
              <div className="rounded-md border border-slate-800">
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-800">
                      <TableHead className="text-slate-300">Name</TableHead>
                      <TableHead className="text-slate-300">Description</TableHead>
                      <TableHead className="text-slate-300">Ω-Score</TableHead>
                      <TableHead className="text-slate-300">Status</TableHead>
                      <TableHead className="text-slate-300">Created</TableHead>
                      <TableHead className="text-slate-300 text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredEntities.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center text-slate-400 py-8">
                          No entities found. Create your first entity!
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredEntities.map((entity) => (
                        <TableRow key={entity.id} className="border-slate-800">
                          <TableCell className="font-medium text-white">
                            {entity.name}
                          </TableCell>
                          <TableCell className="text-slate-300 max-w-md truncate">
                            {entity.description}
                          </TableCell>
                          <TableCell>
                            {getOmegaScoreBadge(entity.omega_score)}
                          </TableCell>
                          <TableCell>
                            {getStatusBadge(entity.status)}
                          </TableCell>
                          <TableCell className="text-slate-400 text-sm">
                            {new Date(entity.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => openEditDialog(entity)}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => deleteEntity(entity.id)}
                              >
                                <Trash2 className="h-4 w-4 text-red-400" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">{entities.length}</div>
                <div className="text-sm text-slate-400">Total Entities</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-500">
                  {entities.filter(e => e.status === 'active').length}
                </div>
                <div className="text-sm text-slate-400">Active</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-500">
                  Ω {(entities.reduce((sum, e) => sum + e.omega_score, 0) / entities.length || 0).toFixed(2)}
                </div>
                <div className="text-sm text-slate-400">Avg Ω-Score</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Base44EntityManager;
