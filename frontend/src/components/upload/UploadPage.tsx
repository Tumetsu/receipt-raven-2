import { Link } from '@tanstack/react-router';
import {
  Camera,
  CheckCircle2,
  FileText,
  ImagePlus,
  Loader2,
  RotateCcw,
  Upload,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState, type ChangeEvent, type DragEvent } from 'react';
import { toast } from 'sonner';

import { apiErrorMessage } from '@/api/errors';
import { PageHeader } from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { useJobMutations } from '@/hooks/useJobs';
import { useSharedFile } from '@/hooks/useSharedFile';
import { cn } from '@/lib/utils';

const ACCEPT = 'image/*,application/pdf';

function isAccepted(file: File): boolean {
  return file.type.startsWith('image/') || file.type === 'application/pdf';
}

/** Show the chosen file: the photo itself, or a PDF card. */
function Preview({ file }: { file: File }) {
  const url = useMemo(() => URL.createObjectURL(file), [file]);
  useEffect(() => () => URL.revokeObjectURL(url), [url]);

  if (file.type === 'application/pdf') {
    return (
      <div className="bg-muted flex flex-col items-center gap-3 rounded-xl p-10 text-center">
        <FileText className="text-destructive size-14" />
        <p className="font-medium break-all">{file.name}</p>
        <a href={url} target="_blank" rel="noreferrer" className="text-primary text-sm font-medium">
          View PDF
        </a>
      </div>
    );
  }
  return (
    <img
      src={url}
      alt="Receipt preview"
      className="bg-muted mx-auto max-h-[60vh] w-full rounded-xl object-contain"
    />
  );
}

function Sent({ onAnother }: { onAnother: () => void }) {
  return (
    <div role="status" className="flex flex-col items-center gap-4 py-10 text-center">
      <CheckCircle2 className="text-success animate-in zoom-in-50 size-20 duration-500" />
      <div>
        <p className="text-lg font-semibold">Receipt sent for analysis</p>
        <p className="text-muted-foreground text-sm">
          It appears under Receipts to review in a moment.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        <Button onClick={onAnother}>
          <Camera /> Upload another
        </Button>
        <Button variant="outline" asChild>
          <Link to="/jobs">Show the queue</Link>
        </Button>
      </div>
    </div>
  );
}

/**
 * Take a photo of a receipt, or pick an image or PDF, and send it for analysis.
 * A file shared from another app (the PWA share target) is preselected.
 */
export function UploadPage({ shared }: { shared: boolean }) {
  const cameraInput = useRef<HTMLInputElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const [chosen, setChosen] = useState<File | null>(null);
  const [sharedDismissed, setSharedDismissed] = useState(false);
  const [sent, setSent] = useState(false);
  const [dragging, setDragging] = useState(false);
  const { uploadReceipt, isUploading } = useJobMutations();
  const sharedFile = useSharedFile(shared);
  // A shared file is offered until the user picks another, retakes or sends it.
  const file = chosen ?? (sharedDismissed ? null : sharedFile);

  const clear = () => {
    setChosen(null);
    setSharedDismissed(true);
  };

  const choose = (picked: File | undefined) => {
    if (!picked) return;
    if (!isAccepted(picked)) {
      toast.error('Choose a photo or a PDF of the receipt.');
      return;
    }
    setChosen(picked);
    setSent(false);
  };

  const onInput = (event: ChangeEvent<HTMLInputElement>) => {
    choose(event.target.files?.[0]);
    event.target.value = '';
  };

  const onDrop = (event: DragEvent) => {
    event.preventDefault();
    setDragging(false);
    choose(event.dataTransfer.files[0]);
  };

  const send = async () => {
    if (!file) return;
    try {
      await uploadReceipt(file);
      clear();
      setSent(true);
    } catch (error) {
      toast.error(apiErrorMessage(error, 'The receipt could not be uploaded.'));
    }
  };

  return (
    <div className="mx-auto max-w-xl">
      <PageHeader
        title="Upload a receipt"
        description="A sharp photo of a flat, well-lit receipt reads best."
      />

      <input
        ref={cameraInput}
        type="file"
        accept={ACCEPT}
        capture="environment"
        className="hidden"
        aria-label="Take a photo"
        onChange={onInput}
      />
      <input
        ref={fileInput}
        type="file"
        accept={ACCEPT}
        className="hidden"
        aria-label="Choose a file"
        onChange={onInput}
      />

      <div className="bg-card rounded-2xl border p-4 shadow-sm sm:p-6">
        {sent ? (
          <Sent onAnother={() => setSent(false)} />
        ) : file ? (
          <div className="flex flex-col gap-4">
            <Preview file={file} />
            <div className="grid grid-cols-2 gap-3">
              <Button variant="outline" size="lg" disabled={isUploading} onClick={clear}>
                <RotateCcw /> Retake
              </Button>
              <Button size="lg" disabled={isUploading} onClick={() => void send()}>
                {isUploading ? <Loader2 className="animate-spin" /> : <Upload />}
                Analyse receipt
              </Button>
            </div>
          </div>
        ) : (
          <div
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={cn(
              'flex flex-col items-center gap-4 rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors',
              dragging && 'border-primary bg-accent/50'
            )}
          >
            <button
              type="button"
              onClick={() => cameraInput.current?.click()}
              className="bg-primary text-primary-foreground grid size-24 place-items-center rounded-full shadow-lg transition-transform hover:scale-105 active:scale-95"
              aria-label="Take a photo"
            >
              <Camera className="size-10" />
            </button>
            <div>
              <p className="font-medium">Take a photo of the receipt</p>
              <p className="text-muted-foreground text-sm">or drop an image or PDF here</p>
            </div>
            <Button variant="outline" onClick={() => fileInput.current?.click()}>
              <ImagePlus /> Choose a file
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
