import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Paper,
  Alert,
  LinearProgress,
} from '@mui/material';
import { formatDate, formatBytes } from '../utils/formatters';
import { useAuth } from '../contexts/AuthContext';

interface DeletionRecord {
  id: string;
  bucket_name: string;
  deleted_at: string;
  size_bytes: number;
  tags: Record<string, string>;
  reason: string;
}

const DeletionHistory: React.FC = () => {
  const { token } = useAuth();
  const [history, setHistory] = useState<DeletionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/deletion-history', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch deletion history');
      }
      
      const data = await response.json();
      setHistory(data.history);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [token]);

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Deletion History
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Bucket Name</TableCell>
                <TableCell>Deleted At</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>Tags</TableCell>
                <TableCell>Reason</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((record) => (
                <TableRow key={record.id}>
                  <TableCell>{record.bucket_name}</TableCell>
                  <TableCell>{formatDate(record.deleted_at)}</TableCell>
                  <TableCell>{formatBytes(record.size_bytes)}</TableCell>
                  <TableCell>
                    {Object.entries(record.tags).map(([key, value]) => (
                      <Typography key={key} variant="body2">
                        {key}: {value}
                      </Typography>
                    ))}
                  </TableCell>
                  <TableCell>{record.reason}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default DeletionHistory; 