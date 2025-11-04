from db_utils import get_collection_stats

stats = get_collection_stats('DSSFull')
print(f"\n📊 Collection: {stats['collection']}")
print(f"Document Count: {stats['document_count']:,}")
print(f"Size: {stats['size_mb']:.2f} MB")
print(f"\n📑 Indexes ({len(stats['indexes'])} total):")
for idx in stats['indexes']:
    print(f"  ✓ {idx['name']}: {idx['keys']}")
