[out:json][timeout:30];
area["name:en"="Sydney"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;