[out:json][timeout:30];
area["name:en"="Bucharest"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;