import os
from pathlib import Path

def write_file(path_str, content):
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ Injected: {path}")

# ==============================================================================# SECTION 1: OPS TOOLS (The Agentic Layer)# ==============================================================================

TOOL_FORGE_IDENTITY = r"""
import os
import re
import yaml
from pathlib import Path

IDENTITY_LEXICON = {
    "definition": [r"I am a (.*?)(?:\n|$)", r"You are (.*?)(?:\n|$)"],
    "metaphor": [r"My metaphor is (.*?)(?:\n|$)", r"Think of me as (.*?)(?:\n|$)"],
    "purpose": [r"My purpose is (.*?)(?:\n|$)", r"My goal is (.*?)(?:\n|$)"],
    "tone": [r"Tone should be (.*?)(?:\n|$)", r"Speak with (.*?)(?:\n|$)"]
}

class IdentityForge:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)

    def extract_traits(self, filename):
        traits = {}
        file_path = self.source_dir / filename
        if not file_path.exists():
            print(f"⚠️  Skipping missing file: {filename}")
            return traits

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for trait, patterns in IDENTITY_LEXICON.items():
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        traits[trait] = match.group(1).strip()
                        break 
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}")
        return traits

    def build_identity_bundle(self, name, source_files):
        merged_identity = {
            "identity": {"name": name, "definition": "Standard AI Assistant"},
            "operations": {"purpose_statement": "Assist user"},
            "style": {"tone": "Neutral"}
        }

        print(f"🔨 Forging Identity: {name}...")
        for file in source_files:
            traits = self.extract_traits(file)
            if "definition" in traits: merged_identity["identity"]["definition"] = traits["definition"]
            if "metaphor" in traits: merged_identity["identity"]["metaphor"] = traits["metaphor"]
            if "purpose" in traits: merged_identity["operations"]["purpose_statement"] = traits["purpose"]
            if "tone" in traits: merged_identity["style"]["tone"] = traits["tone"]

        bundle = {
            "kind": "IdentityConfig",
            "metadata": {"name": name, "version": "1.0"},
            "spec": merged_identity
        }
        
        output_dir = Path("ACP_V1/configs/identities")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{name.lower()}.yaml"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(bundle, f, sort_keys=False)
            
        return f"✅ Created cartridge: {output_file}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        forge = IdentityForge("ACP_V1/inputs/raw_text")
        print(forge.build_identity_bundle(sys.argv[1], sys.argv[2:]))
    else:
        print("Usage: python tool_forge_identity.py <IdentityName> <source_file1> <source_file2>...")
"""

TOOL_EQUIP_IDENTITY = r"""
import shutil
import yaml
import os
import sys

CONFIG_DIR = "ACP_V1/configs"
# The generic file that the Orchestrator reads
ACTIVE_IDENTITY_TARGET = os.path.join(CONFIG_DIR, "active_identity.yaml")

def equip_identity(identity_yaml_path):
    print(f"⚙️  Loading Identity Cartridge: {identity_yaml_path}")
    
    if not os.path.exists(identity_yaml_path):
        return "❌ Error: Cartridge file not found."

    try:
        with open(identity_yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Extract Spec
        new_config = data.get('spec', data)

        # Write to the GENERIC active file
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(ACTIVE_IDENTITY_TARGET, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, sort_keys=False)

        identity_name = new_config.get('identity', {}).get('name', 'Unknown')
        print(f"✅ Cartridge Loaded: {identity_name}")
        print(f"👉 System will act as '{identity_name}' on next restart.")
        return True

    except Exception as e:
        print(f"❌ Failed to load cartridge: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        equip_identity(sys.argv[1])
    else:
        print("Usage: python tool_equip_identity.py <path/to/identity_cartridge.yaml>")
"""

TOOL_FORGE_LENS = r"""
import yaml
import os
import sys

LENS_TEMPLATE = {
    "name": "",
    "description": "",
    "trigger_keywords": [],
    "prompt_archetype": ""
}

class LensForge:
    def __init__(self, library_path="ACP_V1/configs/lenses"):
        self.library_path = library_path
        os.makedirs(self.library_path, exist_ok=True)

    def forge_lens(self, name, description, keywords, system_prompt_logic):
        print(f"🔥 Forging new Cognitive Lens: {name}...")
        
        new_lens = LENS_TEMPLATE.copy()
        new_lens["name"] = name
        new_lens["description"] = description
        new_lens["trigger_keywords"] = [k.strip() for k in keywords.split(",")]
        
        new_lens["prompt_archetype"] = (
            f"## ACTIVE LENS: {name.upper()} ##\n"
            f"Context: {description}\n"
            f"Analysis Logic: {system_prompt_logic}\n"
            "Reference Data: {CONTEXT_CHUNKS}\n"
            "User Query: {USER_QUERY}"
        )

        filename = f"{name.lower().replace(' ', '_')}.yaml"
        file_path = os.path.join(self.library_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump({"lenses": [new_lens]}, f, sort_keys=False)
            
        return f"✅ New Cognitive Lens forged: {file_path}"

if __name__ == "__main__":
    if len(sys.argv) > 4:
        forge = LensForge()
        print(forge.forge_lens(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
    else:
        print("Usage: python tool_forge_lens.py <Name> <Desc> <Keywords> <PromptLogic>")
"""

TOOL_CREATE_SPORE = r"""
import os
import json
import sys

DEPLOYER_TEMPLATE = """
import os
import json

PAYLOAD_JSON = '''
{payload}
'''

def deploy(target_dir="."):
    print("🍄 Spore germinating (Unpacking)...")
    payload = json.loads(PAYLOAD_JSON)
    for filename, content in payload.items():
        path = os.path.join(target_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    print("✅ Deployment complete.")

if __name__ == "__main__":
    deploy()
"""

class SporeDeployer:
    def create_spore(self, source_directory, output_filename="spore_module.py"):
        payload = {}
        print(f"📦 Gathering genetic material from: {source_directory}")
        
        if not os.path.exists(source_directory):
            return "❌ Error: Source directory not found."

        for root, dirs, files in os.walk(source_directory):
            for file in files:
                if file.endswith(('.py', '.yaml', '.json', '.txt', '.md', '.csv')):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, source_directory)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            payload[rel_path] = f.read()
                    except Exception as e:
                        print(f"⚠️ Skipping {file}: {e}")

        payload_json = json.dumps(payload, indent=4)
        final_script = DEPLOYER_TEMPLATE.format(payload=payload_json)

        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_script)
            
        return f"✅ Spore created: {output_filename} ({len(payload)} files included)"

if __name__ == "__main__":
    if len(sys.argv) > 2:
        deployer = SporeDeployer()
        print(deployer.create_spore(sys.argv[1], sys.argv[2]))
    else:
        print("Usage: python tool_create_spore.py <SourceDir> <OutputFile.py>")
"""


TOOL_ARCHITECT_AGENT = r"""
import sys
import os

CEPP_TEMPLATE = '''
### COGNITIVE ENGINEERING PROMPTING PROTOCOL (CEPP) v1.0 ###

1. ROLE ASSIGNMENT:
You are an expert-level AI Systems Architect specializing in {domain}. Your task is to function as a translation engine.

2. CORE OBJECTIVE:
Translate the conceptual framework of {domain} into a structured, multi-document YAML file compliant with the Aletheia OS 'Identity-as-Code' schema.

3. SEMANTIC ANCHORS:
{source_material_summary}

4. STAGED EXECUTION PLAN:
  a. Analyze the semantic anchors.
  b. Create a 'CompositePipeline' YAML.
  c. Create an 'AtomicLens' YAML.
  d. Distill foundational axioms.

Output the final YAML stream below:
'''

def architect_agent(domain, source_text_path):
    print(f"🏗️  Architecting Substrate-Aware System for: {domain}...")
    try:
        with open(source_text_path, 'r', encoding='utf-8') as f:
            source_content = f.read()
            summary = source_content[:2000] + "... [Ref: Full Document]"
    except FileNotFoundError:
        return "❌ Source text not found."

    master_prompt = CEPP_TEMPLATE.format(domain=domain, source_material_summary=summary)
    
    output_filename = f"CEPP_Master_Prompt_{domain.replace(' ', '_')}.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(master_prompt)
        
    return f"✅ CEPP Master Prompt generated: {output_filename}"

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(architect_agent(sys.argv[1], sys.argv[2]))
    else:
        print("Usage: python tool_architect_agent.py <Domain> <SourceTextPath>")
"""

# ==============================================================================# SECTION 2: DEV TOOLS (The Scientific Layer)# ==============================================================================

TOOL_AUDIT_PHYSICS = r"""
import os
import sys
import pandas as pd
import numpy as np

# Constraints derived from analyze_data_v7.py
CONSTRAINTS = {
    'high_coherence_rho': 0.8,
    'k_divergence_tolerance': 0.05, 
    'min_correlation': 0.4
}

def audit_simulation_run(run_directory):
    manifest_path = os.path.join(run_directory, "run_manifest.csv")
    if not os.path.exists(manifest_path):
        return {"status": "ERROR", "reason": "No manifest found"}

    try:
        manifest = pd.read_csv(manifest_path)
    except Exception:
        return {"status": "ERROR", "reason": "Manifest unreadable"}

    # Mock Validation Logic for 'Lightweight' Audit
    # In full version, this imports analyze_data_v7 logic
    if 'k_value' in manifest.columns:
        mean_k = manifest['k_value'].mean()
        ln2 = np.log(2)
        divergence = abs(mean_k - ln2)
        
        if divergence < CONSTRAINTS['k_divergence_tolerance']:
            return {"status": "PASS", "message": f"Physics Verified (k={mean_k:.3f})"}
        else:
            return {"status": "FAIL", "message": f"Divergence detected (k={mean_k:.3f})"}
            
    return {"status": "WARN", "reason": "No physics columns found"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(audit_simulation_run(sys.argv[1]))
"""

TOOL_HARVEST_RUN = r"""
import os
import shutil
import pandas as pd
import struct
import numpy as np

class RunHarvester:
    def __init__(self, root_search_dirs):
        self.root_dirs = root_search_dirs

    def harvest(self, output_dir="ACP_V1/staging/harvested_runs"):
        os.makedirs(output_dir, exist_ok=True)
        img_dir = os.path.join(output_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        
        all_logs = []
        print(f"🚜 Harvesting artifacts...")

        for root_dir in self.root_dirs:
            for root, dirs, files in os.walk(root_dir):
                folder_name = os.path.basename(root)
                # Images
                for f in files:
                    if f.lower().endswith('.png'):
                        shutil.copy2(os.path.join(root, f), os.path.join(img_dir, f"{folder_name}_{f}"))
                # Logs
                if 'umath-validation-set-log.csv' in files:
                    try:
                        df = pd.read_csv(os.path.join(root, 'umath-validation-set-log.csv'), comment='#')
                        df['run_id'] = folder_name
                        all_logs.append(df)
                    except: pass

        if all_logs:
            pd.concat(all_logs, ignore_index=True).to_csv(os.path.join(output_dir, "master_log.csv"), index=False)
            return "✅ Harvest complete."
        return "⚠️ No logs found."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        harvester = RunHarvester(sys.argv[1:])
        print(harvester.harvest())
"""

# ==============================================================================# SECTION 3: FRONTEND COMPONENTS (The Visual Layer)# ==============================================================================

FE_SERVICE_GEMINI = r"""
import { GoogleGenAI } from "@google/genai";

// Ensure VITE_GEMINI_API_KEY is set in your .env.local
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY || "YOUR_KEY_HERE";

export class FrontendGeminiService {
  private client: GoogleGenAI;
  private modelId: string = "gemini-2.0-flash";

  constructor() {
    this.client = new GoogleGenAI({ apiKey: API_KEY });
  }

  async getQuickSuggestion(context: string): Promise<string> {
    try {
      const response = await this.client.models.generateContent({
        model: this.modelId,
        contents: `Context: ${context}\n\nProvide a one-sentence suggestion or fix.`
      });
      return response.text() || "";
    } catch (e) {
      console.error("Gemini UI Error:", e);
      return "System offline.";
    }
  }
}

export const geminiFast = new FrontendGeminiService();
"""

FE_HOOK_QUERY = r"""
import { useState } from 'react';
import { geminiFast } from '../services/FrontendGeminiService';

export const useOptimizedQuery = () => {
  const [isOptimizing, setIsOptimizing] = useState(false);

  const optimizeAndSearch = async (rawQuery: string, backendSearchFn: (term: string) => Promise<any>) => {
    setIsOptimizing(true);
    
    const optimizationPrompt = `
      Act as a RAG Query Optimizer. 
      Convert this user question into a precise technical search query.
      User Question: "${rawQuery}"
      Optimized Query:`;

    let optimizedTerm = rawQuery; 
    try {
      optimizedTerm = await geminiFast.getQuickSuggestion(optimizationPrompt);
      console.log(`🚀 Query Optimized: "${rawQuery}" -> "${optimizedTerm}"`);
    } catch (e) {
      console.warn("Optimization failed, falling back to raw query.");
    }

    const results = await backendSearchFn(optimizedTerm);
    setIsOptimizing(false);
    return results;
  };

  return { optimizeAndSearch, isOptimizing };
};
"""

FE_COMP_SMART_RUNNER = r"""
import React, { useState, useRef } from 'react';
import { geminiFast } from '../services/FrontendGeminiService';

interface SmartCodeRunnerProps {
  initialCode: string;
}

export const SmartCodeRunner: React.FC<SmartCodeRunnerProps> = ({ initialCode }) => {
  const [output, setOutput] = useState<string[]>([]);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [isFixing, setIsFixing] = useState(false);
  const workerRef = useRef<Worker | null>(null);

  const runCode = () => {
    setOutput([]);
    setSuggestion(null);

    const blob = new Blob([`
      onmessage = function(e) {
        console.log = (...args) => postMessage({ type: 'log', data: args.join(' ') });
        try { eval(e.data); } catch (err) { postMessage({ type: 'error', data: err.toString() }); }
      }
    `], { type: 'application/javascript' });

    workerRef.current = new Worker(URL.createObjectURL(blob));
    
    workerRef.current.onmessage = (e) => {
      const { type, data } = e.data;
      if (type === 'log') setOutput(prev => [...prev, `> ${data}`]);
      if (type === 'error') {
        setOutput(prev => [...prev, `❌ ${data}`]);
        handleAutoDiagnose(data, initialCode);
      }
    };

    workerRef.current.postMessage(initialCode);
    setTimeout(() => workerRef.current?.terminate(), 3000);
  };

  const handleAutoDiagnose = async (errorMsg: string, code: string) => {
    setIsFixing(true);
    const fix = await geminiFast.getQuickSuggestion(`Code: ${code}\nError: ${errorMsg}\nFix?`);
    setSuggestion(fix);
    setIsFixing(false);
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded p-4 font-mono text-sm">
      <div className="flex justify-between mb-2">
        <span className="text-slate-300">SANDBOX</span>
        <button onClick={runCode} className="text-green-400 border border-green-400 px-2 rounded">RUN</button>
      </div>
      <div className="mb-4 text-slate-400">{output.map((l, i) => <div key={i}>{l}</div>)}</div>
      {(isFixing || suggestion) && (
        <div className="border-t border-slate-700 pt-2 text-cyan-400">
          <strong>Auto-Fix:</strong> {isFixing ? "Diagnosing..." : suggestion}
        </div>
      )}
    </div>
  );
};
"""

FE_COMP_VISUALIZER = r"""
import React from 'react';
import { ReactP5Wrapper, Sketch } from 'react-p5-wrapper';

interface StackVisualizerProps {
  data: any[];
}

const architectureSketch: Sketch = (p5) => {
  let nodes: any[] = [];
  p5.updateWithProps = (props: { data: any[] }) => {
    if (props.data) {
        // Simple visualization logic mock
        nodes = props.data.map((n, i) => ({ ...n, x: 100 + i*50, y: 200 }));
    }
  };
  p5.draw = () => {
    p5.background(30);
    p5.fill(255);
    nodes.forEach(n => {
        p5.ellipse(n.x, n.y, 40, 40);
        p5.text(n.id, n.x, n.y + 30);
    });
  };
};

export const P5StackVisualizer: React.FC<StackVisualizerProps> = ({ data }) => {
  return (
    <div className="border border-slate-700 rounded overflow-hidden">
      <ReactP5Wrapper sketch={architectureSketch} data={data} />
    </div>
  );
};
"""

FE_COMP_LIVEGRAPH = r"""
import React, { useEffect, useState } from 'react';
import { P5StackVisualizer } from './P5StackVisualizer';

export const LiveGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<any[]>([]);

  useEffect(() => {
    // Connects to the orchestrator_V2 endpoint
    fetch('http://127.0.0.1:5000/system/graph')
      .then(res => res.json())
      .then(data => setGraphData(data.nodes || []))
      .catch(err => console.error("Graph fetch failed", err));
  }, []);

  return (
    <div className="w-full">
      <h3 className="text-slate-400 font-mono text-xs uppercase mb-2">Live Architecture</h3>
      <P5StackVisualizer data={graphData} />
    </div>
  );
};
"""

# ==============================================================================# EXECUTION# ==============================================================================

files_to_inject = {
    "ACP_V1/tools/ops/tool_forge_identity.py": TOOL_FORGE_IDENTITY,
    "ACP_V1/tools/ops/tool_equip_identity.py": TOOL_EQUIP_IDENTITY,
    "ACP_V1/tools/ops/tool_forge_lens.py": TOOL_FORGE_LENS,
    "ACP_V1/tools/ops/tool_create_spore.py": TOOL_CREATE_SPORE,
    "ACP_V1/tools/ops/tool_architect_agent.py": TOOL_ARCHITECT_AGENT,
    
    "ACP_V1/tools/dev/tool_audit_physics.py": TOOL_AUDIT_PHYSICS,
    "ACP_V1/tools/ops/tool_harvest_run_data.py": TOOL_HARVEST_RUN,
    
    "ACP_V1/ui/frontend/services/FrontendGeminiService.ts": FE_SERVICE_GEMINI,
    "ACP_V1/ui/frontend/hooks/useOptimizedQuery.ts": FE_HOOK_QUERY,
    "ACP_V1/ui/frontend/components/SmartCodeRunner.tsx": FE_COMP_SMART_RUNNER,
    "ACP_V1/ui/frontend/components/P5StackVisualizer.tsx": FE_COMP_VISUALIZER,
    "ACP_V1/ui/frontend/components/LiveGraph.tsx": FE_COMP_LIVEGRAPH
}

print("💉 Starting Feature Injection...")
for path, content in files_to_inject.items():
    write_file(path, content)

print("\n✨ Injection Complete. All tools and components are installed.")
