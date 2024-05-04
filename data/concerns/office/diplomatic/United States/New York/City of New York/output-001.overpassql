[out:json][timeout:30000];
area["name"="City of New York"]->.searchArea;
(
  nwr["office"="diplomatic"](area.searchArea);
);
out geom;
