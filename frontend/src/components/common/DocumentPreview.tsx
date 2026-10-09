import { ExternalLink, FileText, ImageOff, Maximize2 } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';

/**
 * The uploaded photo or PDF of a receipt. A photo opens full screen when
 * clicked; a PDF is embedded with a link to open it in a new tab.
 */
export function DocumentPreview({
  url,
  mimeType,
  className,
}: {
  url: string;
  mimeType: string;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const [missing, setMissing] = useState(false);

  if (missing) {
    return (
      <div
        className={cn(
          'text-muted-foreground bg-muted flex flex-col items-center justify-center gap-2 rounded-xl p-8 text-center text-sm',
          className
        )}
      >
        <ImageOff className="size-8" />
        The document is no longer stored.
      </div>
    );
  }

  if (mimeType === 'application/pdf') {
    return (
      <div className={cn('bg-muted flex flex-col overflow-hidden rounded-xl border', className)}>
        <object
          data={url}
          type="application/pdf"
          className="min-h-[60vh] w-full flex-1"
          aria-label="Receipt PDF"
        >
          <div className="flex flex-col items-center gap-2 p-8 text-sm">
            <FileText className="size-8" />
            This browser cannot show PDFs inline.
          </div>
        </object>
        <a
          href={url}
          target="_blank"
          rel="noreferrer"
          className="text-primary flex items-center justify-center gap-1 border-t p-2 text-sm font-medium"
        >
          Open PDF <ExternalLink className="size-3.5" />
        </a>
      </div>
    );
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Show receipt photo full screen"
        className={cn(
          'group bg-muted relative block w-full overflow-hidden rounded-xl border',
          className
        )}
      >
        <img
          src={url}
          alt="Receipt"
          onError={() => setMissing(true)}
          className="mx-auto max-h-[40vh] w-full object-contain lg:max-h-[75vh]"
        />
        <span className="bg-background/80 absolute top-2 right-2 rounded-md p-1.5 opacity-0 shadow-sm backdrop-blur transition-opacity group-hover:opacity-100">
          <Maximize2 className="size-4" />
        </span>
      </button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-h-[95dvh] max-w-[95vw] overflow-auto p-2 sm:max-w-3xl">
          <DialogTitle className="sr-only">Receipt photo</DialogTitle>
          <img src={url} alt="Receipt, full size" className="w-full" />
          <Button variant="secondary" onClick={() => setOpen(false)}>
            Close
          </Button>
        </DialogContent>
      </Dialog>
    </>
  );
}
