[out:json][timeout:30];
area["name:en"="Sydney"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;