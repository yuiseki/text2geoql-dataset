[out:json][timeout:30];
area["name:en"="Bucharest"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;