[out:json][timeout:30];
area["name:en"~"Kanazawa|Yokohama"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
