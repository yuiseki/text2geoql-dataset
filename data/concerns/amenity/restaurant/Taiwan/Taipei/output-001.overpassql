[out:json][timeout:30];
area["name:en"="Taipei"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;