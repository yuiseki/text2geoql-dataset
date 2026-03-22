[out:json][timeout:30];
area["name:en"="Dubai"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;