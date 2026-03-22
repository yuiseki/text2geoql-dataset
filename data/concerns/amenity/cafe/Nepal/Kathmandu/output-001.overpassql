[out:json][timeout:30];
area["name:en"="Kathmandu"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;