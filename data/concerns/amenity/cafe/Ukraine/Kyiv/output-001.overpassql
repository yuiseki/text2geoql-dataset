[out:json][timeout:30];
area["name:en"="Kyiv"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;