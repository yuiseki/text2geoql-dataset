[out:json][timeout:30];
area["name:en"="Dubai"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;