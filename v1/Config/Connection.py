from prisma import Prisma


class PrismaConnection:
    
    def __init__(self) -> None:
        self.prisma = Prisma()
        
        
    async def connect(self) -> None:
        await self.prisma.connect()
        
    async def disconnect(self) -> None:
        await self.prisma.disconnect()
        

prisma_connection = PrismaConnection()
db=prisma_connection.prisma