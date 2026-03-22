[out:json][timeout:30];
area["name:en"="Vancouver"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;