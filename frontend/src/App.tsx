import { useEffect, useMemo, useState } from 'react';
import { Schema, DocCollection, Text } from '@blocksuite/store';
import { AffineSchemas } from '@blocksuite/blocks';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { BlockSuiteEditor } from './components/BlockSuiteEditor';

// Initialize the BlockSuite schema and collection at the top level
const schema = new Schema().register(AffineSchemas);
const collection = new DocCollection({ schema });
collection.meta.initialize();

export default function App() {
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  const [editorMode, setEditorMode] = useState<'page' | 'edgeless'>('page');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Derive the active Doc instance from the collection
  const activeDoc = useMemo(() => {
    if (!activeDocId) return null;
    return collection.getDoc(activeDocId);
  }, [activeDocId, refreshTrigger]);

  // Document creation callback
  const handleCreateDoc = () => {
    const doc = collection.createDoc();
    doc.load();
    
    // Initialize the block tree structure synchronously
    doc.transact(() => {
      // 1. Add the root page container block
      const pageBlockId = doc.addBlock('affine:page', {
        title: new Text('Untitled Document'),
      });
      
      // 2. Add a note container block to hold the text content blocks
      const noteId = doc.addBlock('affine:note', {}, pageBlockId);
      
      // 3. Add an initial paragraph block
      doc.addBlock(
        'affine:paragraph',
        { text: new Text('Start writing here...') },
        noteId
      );
    });

    // Synchronize the workspace metadata title
    collection.meta.setDocMeta(doc.id, { title: 'Untitled Document' });
    
    // Force trigger state update
    setRefreshTrigger(prev => prev + 1);

    // Make the new document active
    setActiveDocId(doc.id);
  };

  // Document deletion callback
  const handleDeleteDoc = (id: string) => {
    collection.removeDoc(id);
    
    // If we deleted the active document, select another one or fallback to null
    if (activeDocId === id) {
      const remainingDocs = collection.meta.docMetas;
      if (remainingDocs.length > 0) {
        setActiveDocId(remainingDocs[0].id);
      } else {
        setActiveDocId(null);
      }
    }
    setRefreshTrigger(prev => prev + 1);
  };

  // Populate first document on application launch if collection is empty
  useEffect(() => {
    if (collection.meta.docMetas.length === 0) {
      handleCreateDoc();
    } else {
      setActiveDocId(collection.meta.docMetas[0].id);
    }
  }, []);

  // Clear current document text blocks
  const handleClearDoc = () => {
    if (!activeDoc) return;
    activeDoc.transact(() => {
      const notes = activeDoc.getBlocksByFlavour('affine:note');
      notes.forEach((note) => {
        activeDoc.deleteBlock(note.model);
      });
      
      // Re-add a default note container block so the editor remains editable
      const rootPage = activeDoc.root;
      if (rootPage) {
        activeDoc.addBlock('affine:note', {}, rootPage.id);
      }
    });
  };

  // Load a set of demo content blocks
  const handleLoadDemo = () => {
    if (!activeDoc) return;

    activeDoc.transact(() => {
      // Clear existing content blocks
      const notes = activeDoc.getBlocksByFlavour('affine:note');
      notes.forEach((note) => {
        activeDoc.deleteBlock(note.model);
      });

      const rootPage = activeDoc.root as any;
      if (!rootPage) return;

      // Update titles
      if (rootPage.title) {
        rootPage.title.clear();
        rootPage.title.insert('✨ BlockSuite Demo Guide', 0);
      }
      collection.meta.setDocMeta(activeDoc.id, { title: '✨ BlockSuite Demo Guide' });

      // Create new note container
      const noteId = activeDoc.addBlock('affine:note', {}, rootPage.id);

      // Append rich demo blocks
      activeDoc.addBlock(
        'affine:paragraph',
        {
          type: 'h1',
          text: new Text('Welcome to the BlockSuite Collaborative Editor!'),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:paragraph',
        {
          text: new Text(
            'This is a fully-featured, rich WYSIWYG editor built using BlockSuite. BlockSuite organizes your document as a tree of collaborative blocks powered by Yjs CRDTs under the hood.'
          ),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:paragraph',
        {
          type: 'h2',
          text: new Text('Supported Block Elements'),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:list',
        {
          type: 'bulleted',
          text: new Text('Structured hierarchically inside parent block containers.'),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:list',
        {
          type: 'bulleted',
          text: new Text('Flexible text styles (H1, H2, Heading, Quote, Bulleted, Numbered, Todo checklists).'),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:list',
        {
          type: 'bulleted',
          text: new Text('Supports switching visual modes: Page layout vs. Edgeless whiteboard canvas!'),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:paragraph',
        {
          type: 'h2',
          text: new Text('TypeScript Initialization Example'),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:code',
        {
          language: 'typescript',
          text: new Text(`// Register block custom elements and boot blocksuite
import { effects } from '@blocksuite/presets';
effects();

import { DocCollection } from '@blocksuite/store';
const collection = new DocCollection();
const doc = collection.createDoc();
console.log('BlockSuite initialized with Doc ID:', doc.id);`),
        },
        noteId
      );

      activeDoc.addBlock('affine:divider', {}, noteId);

      activeDoc.addBlock(
        'affine:list',
        {
          type: 'todo',
          text: new Text('Check out the live statistics dashboard in the header!'),
        },
        noteId
      );

      activeDoc.addBlock(
        'affine:list',
        {
          type: 'todo',
          text: new Text('Toggle the "Edgeless" view in the top right to try the whiteboard canvas.'),
        },
        noteId
      );
    });

    // Force trigger re-render to update stats
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="workspace-container">
      {/* Sidebar navigation panel */}
      <Sidebar
        collection={collection}
        activeDocId={activeDocId}
        onSelectDoc={setActiveDocId}
        onCreateDoc={handleCreateDoc}
        onDeleteDoc={handleDeleteDoc}
      />

      {/* Main editor area */}
      <main className="main-content">
        <Header
          collection={collection}
          doc={activeDoc}
          mode={editorMode}
          onChangeMode={setEditorMode}
          onLoadDemo={handleLoadDemo}
          onClearDoc={handleClearDoc}
        />

        <div className="editor-wrapper">
          {activeDoc ? (
            <BlockSuiteEditor doc={activeDoc} mode={editorMode} />
          ) : (
            <div className="empty-state">
              <span className="empty-state-icon">📝</span>
              <h3>No Document Open</h3>
              <p>Create a new document from the sidebar to begin editing.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
