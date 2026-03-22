[out:json][timeout:30];
area["name:en"="Kyiv"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;