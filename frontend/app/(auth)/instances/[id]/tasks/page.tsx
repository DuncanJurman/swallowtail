import InstanceTasksPageClient from './page-client'

export default async function InstanceTasksPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  
  return <InstanceTasksPageClient instanceId={id} />
}