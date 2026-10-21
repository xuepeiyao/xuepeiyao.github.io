export type Category = 'communication' | 'ui' | 'web' | 'poster' | 'illustration';
export interface Project {
  title: string;
  slug: string;
  category: Category;
  tags: string[];
  year: number | null;
  client: string;
  summary: string;
  role: string;
  background: string;
  goal: string;
  process: string;
  outcome: string;
  cover: string;
  media: {src: string; alt: string; caption: string}[];
  featured: boolean;
  order: number;
  status: 'draft' | 'hidden' | 'public';
  source: 'legacy' | 'provided';
  legacyId?: number;
  notes?: string;
}
