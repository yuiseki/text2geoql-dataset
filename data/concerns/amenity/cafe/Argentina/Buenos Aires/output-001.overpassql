[out:json][timeout:30];
area["name:en"="Buenos Aires"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;