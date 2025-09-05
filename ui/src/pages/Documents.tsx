import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsApi, promptsApi } from '../api/client'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { Button } from '../components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog'
import { Input } from '../components/ui/input'
import { Textarea } from '../components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Toast } from '../components/ui/toast'

export function Documents() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [formData, setFormData] = useState({
    filename: '',
    source_type: '',
    content: ''
  })

  const queryClient = useQueryClient()

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: documentsApi.list
  })

  const createMutation = useMutation({
    mutationFn: documentsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setIsDialogOpen(false)
      setFormData({ filename: '', source_type: '', content: '' })
    }
  })

  const deleteMutation = useMutation({
    mutationFn: documentsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    }
  })

  const generatePromptsMutation = useMutation({
    mutationFn: promptsApi.generateFromDocument,
    onSuccess: () => {
      setToast({
        message: 'Success! Prompt generation has started in the background. New prompts will be available on the Experiments page shortly.',
        type: 'success'
      })
    },
    onError: () => {
      setToast({
        message: 'Failed to start prompt generation. Please try again.',
        type: 'error'
      })
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.filename && formData.source_type && formData.content) {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (docId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(docId)
    }
  }

  const handleGeneratePrompts = (docId: string) => {
    generatePromptsMutation.mutate(docId)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Compliance Docs</h1>
          <p className="text-gray-600">Policy & CTI sources - Manage SOC policies and CTI feeds for adaptive benchmarking</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>Upload Document</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload New Document</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Filename</label>
                <Input
                  value={formData.filename}
                  onChange={(e) => setFormData({ ...formData, filename: e.target.value })}
                  placeholder="document.pdf"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Source Type</label>
                <Select
                  value={formData.source_type}
                  onValueChange={(value) => setFormData({ ...formData, source_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select source type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="GRC_POLICY">GRC Policy</SelectItem>
                    <SelectItem value="CTI_FEED">CTI Feed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Content</label>
                <Textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  placeholder="Document content..."
                  rows={6}
                  required
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Uploading...' : 'Upload'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Document Library</h3>
          
          {isLoading ? (
            <div className="text-center py-8">Loading documents...</div>
          ) : !documents || documents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No documents uploaded yet. Upload your first document to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Filename</TableHead>
                  <TableHead>Source Type</TableHead>
                  <TableHead>Date Added</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.doc_id}>
                    <TableCell className="font-medium">{doc.filename}</TableCell>
                    <TableCell>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        doc.source_type === 'GRC_POLICY' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {doc.source_type === 'GRC_POLICY' ? 'GRC Policy' : 'CTI Feed'}
                      </span>
                    </TableCell>
                    <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleGeneratePrompts(doc.doc_id)}
                          disabled={generatePromptsMutation.isPending}
                        >
                          {generatePromptsMutation.isPending ? 'Generating...' : 'Generate Prompts'}
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(doc.doc_id)}
                          disabled={deleteMutation.isPending}
                        >
                          Delete
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </div>
      
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}