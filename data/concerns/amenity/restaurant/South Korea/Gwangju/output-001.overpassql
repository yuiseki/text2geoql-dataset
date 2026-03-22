[out:json][timeout:30];
area["name:en"="Gwangju"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;