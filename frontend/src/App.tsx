import { Upload } from './components/Upload';
import { Chat } from './components/Chat';

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        
        <header className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
            Synca
          </h1>
          <p className="text-slate-500 mt-2">
            Agente Inteligente
          </p>
        </header>

        <main>
          <Upload />
          <Chat />
        </main>

        <footer className="text-center text-xs text-slate-600 mt-12">
          Desenvolvido por Pablo Ortiz• Powered by Ollama & pgvector
        </footer>
      </div>
    </div>
  )
}

export default App;