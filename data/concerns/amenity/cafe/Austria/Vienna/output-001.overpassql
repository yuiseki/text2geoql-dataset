[out:json][timeout:30];
area["name:en"="Vienna"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;