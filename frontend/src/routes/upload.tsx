import { createFileRoute } from '@tanstack/react-router';

import { UploadPage } from '@/components/upload/UploadPage';

export const Route = createFileRoute('/upload')({
  // `?shared=true`: the service worker received a file from the share sheet.
  validateSearch: (search: Record<string, unknown>): { shared?: boolean } =>
    search.shared === true || search.shared === 'true' ? { shared: true } : {},
  component: function UploadRoute() {
    const { shared } = Route.useSearch();
    return <UploadPage shared={shared === true} />;
  },
});
