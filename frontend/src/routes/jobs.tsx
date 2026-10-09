import { createFileRoute } from '@tanstack/react-router';

import { JobsPage } from '@/components/jobs/JobsPage';
import { optionalPage } from '@/lib/search';

export const Route = createFileRoute('/jobs')({
  validateSearch: (search: Record<string, unknown>): { page?: number } => ({
    page: optionalPage(search.page),
  }),
  component: function JobsRoute() {
    const { page = 1 } = Route.useSearch();
    const navigate = Route.useNavigate();
    return (
      <JobsPage page={page} onPageChange={(next) => void navigate({ search: { page: next } })} />
    );
  },
});
