import { useEffect, useRef } from 'react';
import { Doc } from '@blocksuite/store';
import { AffineEditorContainer } from '@blocksuite/presets';

interface BlockSuiteEditorProps {
  doc: Doc;
  mode: 'page' | 'edgeless';
}

export function BlockSuiteEditor({ doc, mode }: BlockSuiteEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<AffineEditorContainer | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Instantiate the custom BlockSuite editor container
    const editor = new AffineEditorContainer();
    editor.doc = doc;
    editor.mode = mode;
    editorRef.current = editor;

    // Clear previous children and mount the web component
    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(editor);

    return () => {
      // Clean up the web component on unmount or doc change
      editor.remove();
      editorRef.current = null;
    };
  }, [doc]);

  // Handle visual editor mode transitions dynamically
  useEffect(() => {
    if (editorRef.current && editorRef.current.mode !== mode) {
      editorRef.current.mode = mode;
    }
  }, [mode]);

  return <div ref={containerRef} className="editor-mount-point" />;
}
