import React, { useState, useEffect } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Paper, 
  Grid,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import axios from 'axios';

function App() {
  const [buckets, setBuckets] = useState([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);

  const scanBuckets = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/buckets?days=${days}`);
      setBuckets(response.data.candidates_for_deletion);
    } catch (error) {
      console.error('Error scanning buckets:', error);
    }
    setLoading(false);
  };

  const deleteBucket = async (bucketName) => {
    try {
      await axios.delete(`http://localhost:8000/buckets/${bucketName}?dry_run=true`);
      scanBuckets(); // Refresh the list
    } catch (error) {
      console.error('Error deleting bucket:', error);
    }
  };

  return (
    <div>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">
            CRONDA Dashboard
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Bucket Scanner
              </Typography>
              <TextField
                type="number"
                label="Days Threshold"
                value={days}
                onChange={(e) => setDays(e.target.value)}
                sx={{ mr: 2 }}
              />
              <Button 
                variant="contained" 
                onClick={scanBuckets}
                disabled={loading}
              >
                {loading ? 'Scanning...' : 'Scan Buckets'}
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Bucket Name</TableCell>
                    <TableCell>Created At</TableCell>
                    <TableCell>Size (bytes)</TableCell>
                    <TableCell>Tags</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {buckets.map((bucket) => (
                    <TableRow key={bucket.name}>
                      <TableCell>{bucket.name}</TableCell>
                      <TableCell>{new Date(bucket.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>{bucket.size_bytes}</TableCell>
                      <TableCell>{bucket.tags?.join(', ')}</TableCell>
                      <TableCell>
                        <Button
                          variant="outlined"
                          color="error"
                          onClick={() => deleteBucket(bucket.name)}
                        >
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      </Container>
    </div>
  );
}

export default App;