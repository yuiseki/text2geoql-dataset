[out:json][timeout:30];
area["name:en"="Sydney"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;