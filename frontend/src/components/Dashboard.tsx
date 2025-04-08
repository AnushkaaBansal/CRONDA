import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Paper,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import { formatBytes, formatDate } from '../utils/formatters';
import { useAuth } from '../contexts/AuthContext';

interface Bucket {
  name: string;
  created_at: string;
  size_bytes: number;
  location: string;
  storage_class: string;
  labels: Record<string, string>;
}

interface BatchDeleteDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  selectedBuckets: string[];
  dryRun: boolean;
}

const BatchDeleteDialog: React.FC<BatchDeleteDialogProps> = ({
  open,
  onClose,
  onConfirm,
  selectedBuckets,
  dryRun,
}) => (
  <Dialog open={open} onClose={onClose}>
    <DialogTitle>Confirm Batch Delete</DialogTitle>
    <DialogContent>
      <Typography variant="body1">
        {dryRun ? 'Dry Run: Would delete' : 'Delete'} {selectedBuckets.length} bucket(s)?
      </Typography>
      <Box sx={{ mt: 2 }}>
        {selectedBuckets.map((bucket) => (
          <Typography key={bucket} variant="body2">
            • {bucket}
          </Typography>
        ))}
      </Box>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose}>Cancel</Button>
      <Button onClick={onConfirm} color="error" variant="contained">
        {dryRun ? 'Dry Run' : 'Delete'}
      </Button>
    </DialogActions>
  </Dialog>
);

const Dashboard: React.FC = () => {
  const { token } = useAuth();
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBuckets, setSelectedBuckets] = useState<string[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [batchDeleteDialogOpen, setBatchDeleteDialogOpen] = useState(false);
  const [dryRun, setDryRun] = useState(true);
  const [batchOperationProgress, setBatchOperationProgress] = useState(false);

  const fetchBuckets = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/buckets/?days=30', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch buckets');
      }
      
      const data = await response.json();
      setBuckets(data.candidates_for_deletion);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBuckets();
  }, [token]);

  const handleSelectBucket = (bucketName: string) => {
    setSelectedBuckets(prev =>
      prev.includes(bucketName)
        ? prev.filter(name => name !== bucketName)
        : [...prev, bucketName]
    );
  };

  const handleSelectAll = () => {
    setSelectedBuckets(prev =>
      prev.length === buckets.length
        ? []
        : buckets.map(bucket => bucket.name)
    );
  };

  const handleBatchDelete = async () => {
    try {
      setBatchOperationProgress(true);
      const response = await fetch('http://localhost:8000/buckets/batch-delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          bucket_names: selectedBuckets,
          dry_run: dryRun,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to delete buckets');
      }

      const result = await response.json();
      console.log('Batch delete result:', result);
      
      // Refresh the buckets list
      await fetchBuckets();
      setSelectedBuckets([]);
      setBatchDeleteDialogOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete buckets');
    } finally {
      setBatchOperationProgress(false);
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Bucket Management</Typography>
        <Box>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchBuckets} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            color="error"
            disabled={selectedBuckets.length === 0}
            onClick={() => setBatchDeleteDialogOpen(true)}
          >
            Delete Selected ({selectedBuckets.length})
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedBuckets.length === buckets.length}
                      indeterminate={selectedBuckets.length > 0 && selectedBuckets.length < buckets.length}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Storage Class</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {buckets.map((bucket) => (
                  <TableRow key={bucket.name}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedBuckets.includes(bucket.name)}
                        onChange={() => handleSelectBucket(bucket.name)}
                      />
                    </TableCell>
                    <TableCell>{bucket.name}</TableCell>
                    <TableCell>{formatDate(bucket.created_at)}</TableCell>
                    <TableCell>{formatBytes(bucket.size_bytes)}</TableCell>
                    <TableCell>{bucket.location}</TableCell>
                    <TableCell>{bucket.storage_class}</TableCell>
                    <TableCell>
                      <Tooltip title="Delete">
                        <IconButton
                          color="error"
                          onClick={() => {
                            setSelectedBuckets([bucket.name]);
                            setBatchDeleteDialogOpen(true);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <BatchDeleteDialog
        open={batchDeleteDialogOpen}
        onClose={() => setBatchDeleteDialogOpen(false)}
        onConfirm={handleBatchDelete}
        selectedBuckets={selectedBuckets}
        dryRun={dryRun}
      />
    </Box>
  );
};

export default Dashboard;