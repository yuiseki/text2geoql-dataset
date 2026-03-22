[out:json][timeout:30];
area["name:en"="Melbourne"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;