[out:json][timeout:30];
area["name:en"="Athens"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;