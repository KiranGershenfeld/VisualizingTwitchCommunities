from CalculateOverlaps import OverlapsManager
from dotenv import load_dotenv
import os 

if __name__ == "__main__":
    load_dotenv()

    om = OverlapsManager(start_time="", end_time="", db_url=os.environ.get("DB_URL"))
    
    stats = om.calc_stats(9)
    
    print(f"eigenvector_centrality: {stats['eigenvector_centrality'][:5]}")
    print(f"betweeness_centrality: {stats['betweeness_centrality'][:5]}")
    print(f"closeness_centrality: {stats['closeness_centrality'][:5]}")
