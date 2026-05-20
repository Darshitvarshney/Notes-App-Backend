const BASE_URL = 'https://notes-app-backend-ashen.vercel.app';

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'collaborator';
  token: string;
}

export interface Workspace {
  id: string;
  name: string;
  description: string;
  collaborators?: string[];
  notes?: Note[];
  created_at?: string;
  updated_at?: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  author?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SearchResult {
  workspace_id: string;
  workspace_name: string;
  note_id: string;
  title: string;
  content: string;
  tags: string[];
  author?: string;
  created_at?: string;
  updated_at?: string;
}

interface ApiResponse<T = any> {
  message?: string;
  status: number;
  token?: string;
  data?: T;
  total?: number;
  page?: number;
  limit?: number;
}

class ApiService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.getToken()) {
      headers['Authorization'] = `Bearer ${this.getToken()}`;
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok || (data.status && data.status >= 400)) {
      throw new Error(data.message || `Request failed with status ${response.status}`);
    }

    return data;
  }

  // Admin APIs
  async adminSignup(name: string, email: string, password: string) {
    return this.request<{ id: string; name: string; email: string }>('/api/admin/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  }

  async adminLogin(email: string, password: string) {
    return this.request<{ id: string; name: string; email: string }>('/api/admin/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async createWorkspace(name: string, description: string) {
    return this.request('/api/admin/create-workspace', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
  }

  async inviteCollaborator(email: string, workspace_id: string) {
    return this.request('/api/admin/invite-collaborator', {
      method: 'POST',
      body: JSON.stringify({ email, workspace_id }),
    });
  }

  async searchNotes(workspace?: string, note?: string, tags?: string, page: number = 1, limit: number = 10) {
    return this.request<SearchResult[]>('/api/admin/search', {
      method: 'GET',
      body: JSON.stringify({ workspace, note, tags, page, limit }),
    });
  }

  // Collaborator APIs
  async collaboratorSignup(name: string, email: string, password: string) {
    return this.request<{ id: string; name: string; email: string }>('/api/collaborator/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  }

  async collaboratorLogin(email: string, password: string) {
    return this.request<{ id: string; name: string; email: string }>('/api/collaborator/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async getAllWorkspaces() {
    return this.request<Workspace[]>('/api/collaborator/all-workspaces', {
      method: 'GET',
    });
  }

  async getAllNotes(workspace_id: string) {
    return this.request<Note[]>('/api/collaborator/all-notes', {
      method: 'GET',
      body: JSON.stringify({ workspace_id }),
    });
  }

  async createNote(title: string, content: string, tags: string, workspace_id: string) {
    return this.request('/api/collaborator/create-notes', {
      method: 'POST',
      body: JSON.stringify({ title, content, tags, workspace_id }),
    });
  }

  async editNote(note_id: string, title: string, content: string, tags: string, workspace_id: string) {
    return this.request('/api/collaborator/edit-notes', {
      method: 'PUT',
      body: JSON.stringify({ note_id, title, content, tags, workspace_id }),
    });
  }
}

export const api = new ApiService();
