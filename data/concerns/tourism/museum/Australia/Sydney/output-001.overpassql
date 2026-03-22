[out:json][timeout:30];
area["name:en"="Sydney"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;