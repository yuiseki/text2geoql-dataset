[out:json][timeout:30];
area["name:en"="Taipei"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;