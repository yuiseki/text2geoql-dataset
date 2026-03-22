[out:json][timeout:30];
area["name:en"="Busan"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;