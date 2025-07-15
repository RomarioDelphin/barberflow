import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Calendar, 
  Clock, 
  Plus, 
  Edit, 
  CheckCircle, 
  XCircle,
  AlertCircle
} from 'lucide-react';

const Agendamentos = () => {
  const { user, token } = useAuth();
  const [agendamentos, setAgendamentos] = useState([]);
  const [servicos, setServicos] = useState([]);
  const [barbeiros, setBarbeiros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAgendamento, setEditingAgendamento] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    barbeiro_id: '',
    servico_id: '',
    data: '',
    hora: '',
    status: 'pendente'
  });

  useEffect(() => {
    fetchData();
  }, [token]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Buscar agendamentos
      const agendResponse = await fetch('/api/agendamentos/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (agendResponse.ok) {
        const agendData = await agendResponse.json();
        setAgendamentos(agendData);
      }

      // Buscar serviços (para criar novos agendamentos)
      if (user?.tipo === 'cliente') {
        const servicosResponse = await fetch('/api/servicos/');
        if (servicosResponse.ok) {
          const servicosData = await servicosResponse.json();
          setServicos(servicosData);
        }

        const barbeirosResponse = await fetch('/api/barbeiros/');
        if (barbeirosResponse.ok) {
          const barbeirosData = await barbeirosResponse.json();
          setBarbeiros(barbeirosData);
        }
      }
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      setError('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const url = editingAgendamento 
        ? `/api/agendamentos/${editingAgendamento.id}`
        : '/api/agendamentos/';
      
      const method = editingAgendamento ? 'PATCH' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao salvar agendamento');
      }

      setSuccess(editingAgendamento ? 'Agendamento atualizado!' : 'Agendamento criado!');
      setDialogOpen(false);
      setEditingAgendamento(null);
      setFormData({
        barbeiro_id: '',
        servico_id: '',
        data: '',
        hora: '',
        status: 'pendente'
      });
      fetchData();
    } catch (error) {
      setError(error.message);
    }
  };

  const handleEdit = (agendamento) => {
    setEditingAgendamento(agendamento);
    setFormData({
      barbeiro_id: agendamento.barbeiro_id.toString(),
      servico_id: agendamento.servico_id.toString(),
      data: agendamento.data,
      hora: agendamento.hora,
      status: agendamento.status
    });
    setDialogOpen(true);
  };

  const handleStatusChange = async (agendamentoId, newStatus) => {
    try {
      const response = await fetch(`/api/agendamentos/${agendamentoId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao atualizar status');
      }

      setSuccess('Status atualizado!');
      fetchData();
    } catch (error) {
      setError(error.message);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'pendente': 'secondary',
      'confirmado': 'default',
      'realizado': 'success',
      'cancelado': 'destructive'
    };
    
    return (
      <Badge variant={variants[status] || 'secondary'}>
        {status}
      </Badge>
    );
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'confirmado':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'realizado':
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case 'cancelado':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Carregando agendamentos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {user?.tipo === 'cliente' ? 'Meus Agendamentos' : 'Agendamentos'}
          </h1>
          <p className="text-gray-600">
            {user?.tipo === 'cliente' 
              ? 'Gerencie seus agendamentos e agende novos serviços'
              : 'Visualize e gerencie todos os agendamentos'
            }
          </p>
        </div>
        
        {user?.tipo === 'cliente' && (
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center space-x-2">
                <Plus className="h-4 w-4" />
                <span>Novo Agendamento</span>
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingAgendamento ? 'Editar Agendamento' : 'Novo Agendamento'}
                </DialogTitle>
                <DialogDescription>
                  Preencha os dados para {editingAgendamento ? 'atualizar' : 'criar'} o agendamento.
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="servico">Serviço</Label>
                  <Select 
                    value={formData.servico_id} 
                    onValueChange={(value) => setFormData({...formData, servico_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um serviço" />
                    </SelectTrigger>
                    <SelectContent>
                      {servicos.map((servico) => (
                        <SelectItem key={servico.id} value={servico.id.toString()}>
                          {servico.nome} - R$ {servico.preco.toFixed(2)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="barbeiro">Barbeiro</Label>
                  <Select 
                    value={formData.barbeiro_id} 
                    onValueChange={(value) => setFormData({...formData, barbeiro_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um barbeiro" />
                    </SelectTrigger>
                    <SelectContent>
                      {barbeiros.map((barbeiro) => (
                        <SelectItem key={barbeiro.id} value={barbeiro.id.toString()}>
                          {barbeiro.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="data">Data</Label>
                    <Input
                      id="data"
                      type="date"
                      value={formData.data}
                      onChange={(e) => setFormData({...formData, data: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="hora">Hora</Label>
                    <Input
                      id="hora"
                      type="time"
                      value={formData.hora}
                      onChange={(e) => setFormData({...formData, hora: e.target.value})}
                      required
                    />
                  </div>
                </div>

                {editingAgendamento && (
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select 
                      value={formData.status} 
                      onValueChange={(value) => setFormData({...formData, status: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pendente">Pendente</SelectItem>
                        <SelectItem value="confirmado">Confirmado</SelectItem>
                        <SelectItem value="realizado">Realizado</SelectItem>
                        <SelectItem value="cancelado">Cancelado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <div className="flex justify-end space-x-2">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => setDialogOpen(false)}
                  >
                    Cancelar
                  </Button>
                  <Button type="submit">
                    {editingAgendamento ? 'Atualizar' : 'Criar'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {success && (
        <Alert>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4">
        {agendamentos.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Nenhum agendamento encontrado</p>
            </CardContent>
          </Card>
        ) : (
          agendamentos.map((agendamento) => (
            <Card key={agendamento.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(agendamento.status)}
                    <div>
                      <h3 className="font-semibold text-lg">
                        {agendamento.servico_nome}
                      </h3>
                      <p className="text-gray-600">
                        {user?.tipo !== 'cliente' && `Cliente: ${agendamento.cliente_nome} • `}
                        {user?.tipo !== 'barbeiro' && `Barbeiro: ${agendamento.barbeiro_nome} • `}
                        {agendamento.data} às {agendamento.hora}
                      </p>
                      {agendamento.valor_final && (
                        <p className="text-sm text-gray-500">
                          Valor: R$ {agendamento.valor_final.toFixed(2)}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {getStatusBadge(agendamento.status)}
                    
                    {(user?.tipo === 'barbeiro' || user?.tipo === 'gerente') && (
                      <div className="flex space-x-1">
                        {agendamento.status === 'pendente' && (
                          <Button
                            size="sm"
                            onClick={() => handleStatusChange(agendamento.id, 'confirmado')}
                          >
                            Confirmar
                          </Button>
                        )}
                        {agendamento.status === 'confirmado' && (
                          <Button
                            size="sm"
                            onClick={() => handleStatusChange(agendamento.id, 'realizado')}
                          >
                            Finalizar
                          </Button>
                        )}
                      </div>
                    )}
                    
                    {user?.tipo === 'cliente' && agendamento.status === 'pendente' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(agendamento)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default Agendamentos;

