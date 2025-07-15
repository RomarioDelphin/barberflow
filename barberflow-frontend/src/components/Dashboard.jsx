import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Calendar, 
  DollarSign, 
  Users, 
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

const Dashboard = () => {
  const { user, token } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [agendamentos, setAgendamentos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Buscar dados do dashboard (apenas para gerentes)
        if (user?.tipo === 'gerente') {
          const dashResponse = await fetch('/api/financeiro/dashboard', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (dashResponse.ok) {
            const dashData = await dashResponse.json();
            setDashboardData(dashData);
          }
        }

        // Buscar agendamentos
        const agendResponse = await fetch('/api/agendamentos/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (agendResponse.ok) {
          const agendData = await agendResponse.json();
          setAgendamentos(agendData.slice(0, 5)); // Últimos 5 agendamentos
        }
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchData();
    }
  }, [token, user]);

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

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmado':
        return 'text-green-700 bg-green-50';
      case 'realizado':
        return 'text-blue-700 bg-blue-50';
      case 'cancelado':
        return 'text-red-700 bg-red-50';
      default:
        return 'text-yellow-700 bg-yellow-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Bem-vindo, {user?.nome}!
        </h1>
        <p className="text-gray-600">
          {user?.tipo === 'gerente' && 'Gerencie sua barbearia com facilidade'}
          {user?.tipo === 'barbeiro' && 'Acompanhe sua agenda e atendimentos'}
          {user?.tipo === 'cliente' && 'Gerencie seus agendamentos'}
        </p>
      </div>

      {/* Cards de estatísticas (apenas para gerentes) */}
      {user?.tipo === 'gerente' && dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Receita do Mês</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                R$ {dashboardData.receita_mes?.toFixed(2) || '0,00'}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Receita Hoje</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                R$ {dashboardData.receita_hoje?.toFixed(2) || '0,00'}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Gastos do Mês</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                R$ {dashboardData.gastos_mes?.toFixed(2) || '0,00'}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Lucro do Mês</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                R$ {dashboardData.lucro_mes?.toFixed(2) || '0,00'}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Agendamentos recentes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5" />
            <span>
              {user?.tipo === 'gerente' && 'Agendamentos Recentes'}
              {user?.tipo === 'barbeiro' && 'Meus Próximos Agendamentos'}
              {user?.tipo === 'cliente' && 'Meus Agendamentos'}
            </span>
          </CardTitle>
          <CardDescription>
            Últimos agendamentos do sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          {agendamentos.length === 0 ? (
            <p className="text-gray-500 text-center py-4">
              Nenhum agendamento encontrado
            </p>
          ) : (
            <div className="space-y-4">
              {agendamentos.map((agendamento) => (
                <div
                  key={agendamento.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(agendamento.status)}
                    <div>
                      <p className="font-medium">
                        {agendamento.servico_nome}
                      </p>
                      <p className="text-sm text-gray-600">
                        {user?.tipo !== 'cliente' && `Cliente: ${agendamento.cliente_nome} • `}
                        {user?.tipo !== 'barbeiro' && `Barbeiro: ${agendamento.barbeiro_nome} • `}
                        {agendamento.data} às {agendamento.hora}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agendamento.status)}`}>
                      {agendamento.status}
                    </span>
                    {agendamento.valor_final && (
                      <p className="text-sm text-gray-600 mt-1">
                        R$ {agendamento.valor_final.toFixed(2)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

