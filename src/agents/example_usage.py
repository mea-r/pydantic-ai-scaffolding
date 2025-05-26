"""Example usage of the new agent system"""
import asyncio
from pathlib import Path

# Import the AI helper (your existing class)
import sys
sys.path.append(str(Path(__file__).parent.parent))
from ai_helper import AiHelper

# Import the new agent system
from agents import ContentEditingWorkflow
from agents.registry.agent_registry import get_registry


async def example_workflow():
    """Example of using the content editing workflow"""
    
    # Initialize your AI helper
    ai_helper = AiHelper()
    
    # Create the workflow
    workflow = ContentEditingWorkflow(ai_helper)
    
    # Run the workflow on a file
    file_path = "example_document.txt"  # Replace with actual file
    
    try:
        result = await workflow.run_and_display(file_path)
        print("\n🎉 Workflow completed successfully!")
        
        # Access individual results
        original = result['original_content']
        final_edit = result['final_edit']
        feedback = result['final_feedback']
        
        print(f"\nOriginal file type: {original.file_type}")
        print(f"Key points: {original.key_points}")
        print(f"Changes made: {final_edit.changes_made}")
        print(f"Quality score: {feedback.quality_score:.2f}")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")


async def example_individual_agents():
    """Example of using individual agents"""
    
    ai_helper = AiHelper()
    registry = get_registry()
    
    # Create individual agents using the registry
    file_processor = registry.create_agent('file_processor', ai_helper)
    text_editor = registry.create_agent('text_editor', ai_helper)
    
    # Use them individually
    file_path = "example_document.txt"
    
    print(f"📁 Processing file: {file_path}")
    # Process file
    processed = await file_processor.process_file(file_path)
    print(f"✅ Processed: {processed.summary}")
    
    print(f"✏️ Editing content...")
    # Edit content
    edited = await text_editor.edit_content(processed.extracted_text)
    print(f"✅ Edited with {len(edited.changes_made)} changes")


def list_available_agents():
    """Show available agents and their info"""
    registry = get_registry()
    
    print("Available agents:")
    for agent_name in registry.list_agents():
        info = registry.get_agent_info(agent_name)
        print(f"  - {agent_name}: {info.get('description', 'No description')}")


async def main_agent_example():
    """Main async function to run examples"""
    print("🤖 Agent System Example")
    print("=" * 50)
    
    # Show available agents
    list_available_agents()
    
    print("\n🔄 Running workflow example...")
    await example_workflow()
    
    print("\n🔧 Running individual agent example...")
    await example_individual_agents()


if __name__ == "__main__":
    asyncio.run(main_agent_example())
