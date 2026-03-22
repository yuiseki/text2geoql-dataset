[out:json][timeout:30];
area["name:en"="Helsinki"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;