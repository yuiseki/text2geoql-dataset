[out:json][timeout:30000];
area["name"="City of New York"]->.searchArea;
(
  nwr["leisure"="park"](area.searchArea);
);
out geom;
