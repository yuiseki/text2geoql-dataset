[out:json][timeout:30000];
area["name:en"="Ishikawa Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Kanazawa"](area.searchArea);
);
out geom;
