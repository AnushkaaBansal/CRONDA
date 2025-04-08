import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useAuth } from '../contexts/AuthContext';

interface TagManagerProps {
  bucketName: string;
  tags: Record<string, string>;
  onUpdate: (newTags: Record<string, string>) => void;
}

const TagManager: React.FC<TagManagerProps> = ({ bucketName, tags, onUpdate }) => {
  const { token } = useAuth();
  const [open, setOpen] = useState(false);
  const [newTag, setNewTag] = useState({ key: '', value: '' });
  const [error, setError] = useState<string | null>(null);

  const handleAddTag = async () => {
    if (!newTag.key || !newTag.value) {
      setError('Both key and value are required');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/buckets/${bucketName}/tags`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          key: newTag.key,
          value: newTag.value,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add tag');
      }

      const updatedTags = { ...tags, [newTag.key]: newTag.value };
      onUpdate(updatedTags);
      setOpen(false);
      setNewTag({ key: '', value: '' });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add tag');
    }
  };

  const handleDeleteTag = async (key: string) => {
    try {
      const response = await fetch(`http://localhost:8000/buckets/${bucketName}/tags/${key}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete tag');
      }

      const { [key]: _, ...remainingTags } = tags;
      onUpdate(remainingTags);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete tag');
    }
  };

  return (
    <>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
        {Object.entries(tags).map(([key, value]) => (
          <Chip
            key={key}
            label={`${key}: ${value}`}
            onDelete={() => handleDeleteTag(key)}
            deleteIcon={<DeleteIcon />}
          />
        ))}
        <Tooltip title="Add Tag">
          <IconButton onClick={() => setOpen(true)} color="primary">
            <AddIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Add New Tag</DialogTitle>
        <DialogContent>
          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Key"
            fullWidth
            value={newTag.key}
            onChange={(e) => setNewTag({ ...newTag, key: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Value"
            fullWidth
            value={newTag.value}
            onChange={(e) => setNewTag({ ...newTag, value: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleAddTag} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default TagManager; 