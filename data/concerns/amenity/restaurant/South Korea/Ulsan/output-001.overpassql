[out:json][timeout:30];
area["name:en"="Ulsan"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;