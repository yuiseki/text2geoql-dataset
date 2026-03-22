[out:json][timeout:30];
area["name:en"="Ulsan"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;